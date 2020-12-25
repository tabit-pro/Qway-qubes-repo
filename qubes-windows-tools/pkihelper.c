#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <getopt.h>
#include <wincrypt.h>
#include <wintrust.h>
#include <mssign32.h>
#include <mscat.h>
#include <shlwapi.h>
#include <stringapiset.h>
#ifdef __MINGW32__
#include <mscat_ext.h>
#endif
#include <stdint.h>
#include <ctype.h>
#include <strsafe.h>

static int opt_silent = 1;

#define size_t SIZE_T
#define ssize_t SSIZE_T

#define oprintf(...) do {if (!opt_silent) { printf(__VA_ARGS__); printf("\n"); }} while(0)

#define safe_strlen(str) ((((char*)str)==NULL)?0:strlen(str))
#define static_sprintf(dest, format, ...) StringCbPrintfA(dest, sizeof(dest), format, __VA_ARGS__)

#define STR_BUFFER_SIZE             256

#define KEY_CONTAINER               L"qvideo key container"

/*
 * The following is the data Microsoft adds on the
 * SPC_SP_OPUS_INFO_OBJID and SPC_STATEMENT_TYPE_OBJID OIDs
 */
#define SP_OPUS_INFO_DATA       { 0x30, 0x00 }
#define STATEMENT_TYPE_DATA     { 0x30, 0x0c, 0x06, 0x0a, 0x2b, 0x06, 0x01, 0x04, 0x01, 0x82, 0x37, 0x02, 0x01, 0x15}

/*
 * WinTrust.dll
 */
#define SHA1_HASH_LENGTH				20

static char *windows_error_str(uint32_t retval)
{
	static char err_string[STR_BUFFER_SIZE];

        DWORD size;
        ssize_t i;
        uint32_t error_code, format_error;

        error_code = retval?retval:GetLastError();

        StringCchPrintfA(err_string, STR_BUFFER_SIZE, "[%u] ", error_code);

        // Translate codes returned by SetupAPI. The ones we are dealing with are either
        // in 0x0000xxxx or 0xE000xxxx and can be distinguished from standard error codes.
        // See http://msdn.microsoft.com/en-us/library/windows/hardware/ff545011.aspx
        switch (error_code & 0xE0000000) {
        case 0:
                error_code = HRESULT_FROM_WIN32(error_code);    // Still leaves ERROR_SUCCESS unmodified
                break;
        case 0xE0000000:
                error_code =  0x80000000 | (FACILITY_SETUPAPI << 16) | (error_code & 0x0000FFFF);
                break;
        default:
                break;
        }

        size = FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM, NULL, error_code,
                MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), &err_string[safe_strlen(err_string)],
                STR_BUFFER_SIZE - (DWORD)safe_strlen(err_string), NULL);
        if (size == 0) {
                format_error = GetLastError();
                if (format_error)
                        StringCchPrintfA(err_string, STR_BUFFER_SIZE,
                                "Windows error code %u (FormatMessage error code %u)", error_code, format_error);
                else
                        StringCchPrintfA(err_string, STR_BUFFER_SIZE, "Unknown error code %u", error_code);
        } else {
                // Remove CR/LF terminators
                for (i=(ssize_t)safe_strlen(err_string)-1; (i>=0) && ((err_string[i]==0x0A) || (err_string[i]==0x0D)); i--) {
                        err_string[i] = 0;
                }
        }
        return err_string;
}


/*
 * FormatMessage does not handle PKI errors
 */
char* winpki_error_str(uint32_t retval)
{
	static char error_string[64];
	uint32_t error_code = retval ? retval : GetLastError();

	if ((error_code >> 16) != 0x8009)
		return windows_error_str(error_code);

	switch (error_code) {
	case NTE_BAD_UID:
		return "Bad UID.";
	case CRYPT_E_MSG_ERROR:
		return "An error occurred while performing an operation on a cryptographic message.";
	case CRYPT_E_UNKNOWN_ALGO:
		return "Unknown cryptographic algorithm.";
	case CRYPT_E_INVALID_MSG_TYPE:
		return "Invalid cryptographic message type.";
	case CRYPT_E_HASH_VALUE:
		return "The hash value is not correct";
	case CRYPT_E_ISSUER_SERIALNUMBER:
		return "Invalid issuer and/or serial number.";
	case CRYPT_E_BAD_LEN:
		return "The length specified for the output data was insufficient.";
	case CRYPT_E_BAD_ENCODE:
		return "An error occurred during encode or decode operation.";
	case CRYPT_E_FILE_ERROR:
		return "An error occurred while reading or writing to a file.";
	case CRYPT_E_NOT_FOUND:
		return "Cannot find object or property.";
	case CRYPT_E_EXISTS:
		return "The object or property already exists.";
	case CRYPT_E_NO_PROVIDER:
		return "No provider was specified for the store or object.";
	case CRYPT_E_DELETED_PREV:
		return "The previous certificate or CRL context was deleted.";
	case CRYPT_E_NO_MATCH:
		return "Cannot find the requested object.";
	case CRYPT_E_UNEXPECTED_MSG_TYPE:
	case CRYPT_E_NO_KEY_PROPERTY:
	case CRYPT_E_NO_DECRYPT_CERT:
		return "Private key or certificate issue";
	case CRYPT_E_BAD_MSG:
		return "Not a cryptographic message.";
	case CRYPT_E_NO_SIGNER:
		return "The signed cryptographic message does not have a signer for the specified signer index.";
	case CRYPT_E_REVOKED:
		return "The certificate is revoked.";
	case CRYPT_E_NO_REVOCATION_DLL:
	case CRYPT_E_NO_REVOCATION_CHECK:
	case CRYPT_E_REVOCATION_OFFLINE:
	case CRYPT_E_NOT_IN_REVOCATION_DATABASE:
		return "Cannot check certificate revocation.";
	case CRYPT_E_INVALID_NUMERIC_STRING:
	case CRYPT_E_INVALID_PRINTABLE_STRING:
	case CRYPT_E_INVALID_IA5_STRING:
	case CRYPT_E_INVALID_X500_STRING:
	case  CRYPT_E_NOT_CHAR_STRING:
		return "Invalid string.";
	case CRYPT_E_SECURITY_SETTINGS:
		return "The cryptographic operation failed due to a local security option setting.";
	case CRYPT_E_NO_VERIFY_USAGE_CHECK:
	case CRYPT_E_VERIFY_USAGE_OFFLINE:
		return "Cannot complete usage check.";
	case CRYPT_E_NO_TRUSTED_SIGNER:
		return "None of the signers of the cryptographic message or certificate trust list is trusted.";
	default:
		static_sprintf(error_string, "Unknown PKI error 0x%08X", error_code);
		return error_string;
	}
}

/*
 * Remove a certificate, identified by its subject, to the system store 'szStoreName'
 */
BOOL RemoveCertFromStore(LPCSTR szCertSubject, LPCSTR szStoreName)
{
	HCERTSTORE hSystemStore = NULL;
	PCCERT_CONTEXT pCertContext;
	CERT_NAME_BLOB certNameBlob = {0, NULL};
	BOOL r = FALSE;

	hSystemStore = CertOpenStore(CERT_STORE_PROV_SYSTEM_A, X509_ASN_ENCODING,
		0, CERT_SYSTEM_STORE_LOCAL_MACHINE, szStoreName);
	if (hSystemStore == NULL) {
		oprintf("failed to open system store '%s': %s", szStoreName, winpki_error_str(0));
		goto out;
	}

	// Encode Cert Name
	if ( (!CertStrToNameA(X509_ASN_ENCODING, szCertSubject, CERT_X500_NAME_STR, NULL, NULL, &certNameBlob.cbData, NULL))
	  || ((certNameBlob.pbData = (BYTE*)malloc(certNameBlob.cbData)) == NULL)
	  || (!CertStrToNameA(X509_ASN_ENCODING, szCertSubject, CERT_X500_NAME_STR, NULL, certNameBlob.pbData, &certNameBlob.cbData, NULL)) ) {
		oprintf("failed to encode'%s': %s", szCertSubject, winpki_error_str(0));
		goto out;
	}

	pCertContext = NULL;
	while ((pCertContext = CertFindCertificateInStore(hSystemStore, X509_ASN_ENCODING, 0,
		CERT_FIND_SUBJECT_NAME, (const void*)&certNameBlob, NULL)) != NULL) {
		CertDeleteCertificateFromStore(pCertContext);
		oprintf("deleted existing certificate '%s' from '%s' store", szCertSubject, szStoreName);
	}
	r = TRUE;

out:
	free(certNameBlob.pbData);
	if (hSystemStore != NULL)
		CertCloseStore(hSystemStore, 0);
	return r;
}

/*
 * Add certificate data to the TrustedPublisher system store
 * Unless bDisableWarning is set, warn the user before install
 */
BOOL AddCertToTrustedPublisher(BYTE* pbCertData, DWORD dwCertSize, BOOL bDisableWarning, HWND hWnd)
{
	BOOL r = FALSE;
	int user_input;
	HCERTSTORE hSystemStore = NULL;
	PCCERT_CONTEXT pCertContext = NULL, pStoreCertContext = NULL;
	char org[MAX_PATH], org_unit[MAX_PATH];
	char msg_string[1024];

	hSystemStore = CertOpenStore(CERT_STORE_PROV_SYSTEM_A, X509_ASN_ENCODING,
		0, CERT_SYSTEM_STORE_LOCAL_MACHINE, "TrustedPublisher");

	if (hSystemStore == NULL) {
		oprintf("unable to open system store: %s", winpki_error_str(0));
		goto out;
	}

	/* Check whether certificate already exists
	 * We have to do this manually, so that we can produce a warning to the user
	 * before any certificate is added to the store (first time or update)
	 */
	pCertContext = CertCreateCertificateContext(X509_ASN_ENCODING, pbCertData, dwCertSize);

	if (pCertContext == NULL) {
		oprintf("could not create context for certificate: %s", winpki_error_str(0));
		CertCloseStore(hSystemStore, 0);
		goto out;
	}

	pStoreCertContext = CertFindCertificateInStore(hSystemStore, X509_ASN_ENCODING, 0,
		CERT_FIND_EXISTING, (const void*)pCertContext, NULL);
	if (pStoreCertContext == NULL) {
		user_input = IDOK;
		if (!bDisableWarning) {
			org[0] = 0; org_unit[0] = 0;
			CertGetNameStringA(pCertContext, CERT_NAME_ATTR_TYPE, 0, szOID_ORGANIZATION_NAME, org, sizeof(org));
			CertGetNameStringA(pCertContext, CERT_NAME_ATTR_TYPE, 0, szOID_ORGANIZATIONAL_UNIT_NAME, org_unit, sizeof(org_unit));
			static_sprintf(msg_string, "Warning: this software is about to install the following organization\n"
				"as a Trusted Publisher on your system:\n\n '%s%s%s%s'\n\n"
				"This will allow this Publisher to run software with elevated privileges,\n"
				"as well as install driver packages, without further security notices.\n\n"
				"If this is not what you want, you can cancel this operation now.", org,
				(org_unit[0] != 0)?" (":"", org_unit, (org_unit[0] != 0)?")":"");
				user_input = MessageBoxA(hWnd, msg_string,
					"Warning: Trusted Certificate installation", MB_OKCANCEL | MB_ICONWARNING);
		}
		if (user_input != IDOK) {
			oprintf("operation cancelled by the user");
		} else {
			if (!CertAddCertificateContextToStore(hSystemStore, pCertContext, CERT_STORE_ADD_NEWER, NULL)) {
				oprintf("could not add certificate: %s", winpki_error_str(0));
			} else {
				r = TRUE;
			}
		}
	} else {
		r = TRUE;	// Cert already exists
	}

out:
	if (pCertContext != NULL)
		CertFreeCertificateContext(pCertContext);
	if (pStoreCertContext != NULL)
		CertFreeCertificateContext(pStoreCertContext);
	if (hSystemStore)
		CertCloseStore(hSystemStore, 0);
	return r;
}

/*
 * Create a self signed certificate for code signing
 */
PCCERT_CONTEXT CreateSelfSignedCert(LPCSTR szCertSubject)
{
	DWORD dwSize;
	HCRYPTPROV hCSP = 0;
	HCRYPTKEY hKey = 0;
	PCCERT_CONTEXT pCertContext = NULL;
	CERT_NAME_BLOB SubjectIssuerBlob = {0, NULL};
	CRYPT_KEY_PROV_INFO KeyProvInfo;
	CRYPT_ALGORITHM_IDENTIFIER SignatureAlgorithm;
	LPWSTR wszKeyContainer = KEY_CONTAINER;
	LPBYTE pbEnhKeyUsage = NULL, pbAltNameInfo = NULL, pbCPSNotice = NULL, pbPolicyInfo = NULL;
	SYSTEMTIME sExpirationDate = { 2029, 01, 01, 01, 00, 00, 00, 000 };
	CERT_EXTENSION certExtension[3];
	CERT_EXTENSIONS certExtensionsArray;
	// Code Signing Enhanced Key Usage
	LPSTR szCertPolicyElementId = "1.3.6.1.5.5.7.3.3"; // szOID_PKIX_KP_CODE_SIGNING;
	CERT_ENHKEY_USAGE certEnhKeyUsage = { 1, &szCertPolicyElementId };
	// Alternate Name (URL)
	CERT_ALT_NAME_ENTRY certAltNameEntry = { CERT_ALT_NAME_URL, {.pwszURL = L"http://qvideo.qubes-os.org"} };
	CERT_ALT_NAME_INFO certAltNameInfo = { 1, &certAltNameEntry };
	// Certificate Policies
	CERT_POLICY_QUALIFIER_INFO certPolicyQualifier;
	CERT_POLICY_INFO certPolicyInfo = { "1.3.6.1.5.5.7.2.1", 1, &certPolicyQualifier };
	CERT_POLICIES_INFO certPolicyInfoArray = { 1, &certPolicyInfo };
	CHAR szCPSName[] = "http://qvideo-cps.qubes-os.org";
	CERT_NAME_VALUE certCPSValue;

	// Set Enhanced Key Usage extension to Code Signing only
	if ( (!CryptEncodeObject(X509_ASN_ENCODING, X509_ENHANCED_KEY_USAGE, (LPVOID)&certEnhKeyUsage, NULL, &dwSize))
	  || ((pbEnhKeyUsage = (BYTE*)malloc(dwSize)) == NULL)
	  || (!CryptEncodeObject(X509_ASN_ENCODING, X509_ENHANCED_KEY_USAGE, (LPVOID)&certEnhKeyUsage, pbEnhKeyUsage, &dwSize)) ) {
		oprintf("could not setup EKU for code signing: %s", winpki_error_str(0));
		goto out;
	}
	certExtension[0].pszObjId = szOID_ENHANCED_KEY_USAGE;
	certExtension[0].fCritical = TRUE;		// only allow code signing
	certExtension[0].Value.cbData = dwSize;
	certExtension[0].Value.pbData = pbEnhKeyUsage;

	// Set URL as Alt Name parameter
	if ( (!CryptEncodeObject(X509_ASN_ENCODING, X509_ALTERNATE_NAME, (LPVOID)&certAltNameInfo, NULL, &dwSize))
	  || ((pbAltNameInfo = (BYTE*)malloc(dwSize)) == NULL)
	  || (!CryptEncodeObject(X509_ASN_ENCODING, X509_ALTERNATE_NAME, (LPVOID)&certAltNameInfo, pbAltNameInfo, &dwSize)) ) {
		oprintf("could not setup URL: %s", winpki_error_str(0));
		goto out;
	}
	certExtension[1].pszObjId = szOID_SUBJECT_ALT_NAME;
	certExtension[1].fCritical = FALSE;
	certExtension[1].Value.cbData = dwSize;
	certExtension[1].Value.pbData = pbAltNameInfo;

	// Set the CPS Certificate Policies field - this enables the "Issuer Statement" button on the cert
	certCPSValue.dwValueType = CERT_RDN_IA5_STRING;
	certCPSValue.Value.cbData = sizeof(szCPSName);
	certCPSValue.Value.pbData = (BYTE*)szCPSName;
	if ( (!CryptEncodeObject(X509_ASN_ENCODING, X509_NAME_VALUE, (LPVOID)&certCPSValue, NULL, &dwSize))
		|| ((pbCPSNotice = (BYTE*)malloc(dwSize)) == NULL)
		|| (!CryptEncodeObject(X509_ASN_ENCODING, X509_NAME_VALUE, (LPVOID)&certCPSValue, pbCPSNotice, &dwSize)) ) {
		oprintf("could not setup CPS: %s", winpki_error_str(0));
		goto out;
	}

	certPolicyQualifier.pszPolicyQualifierId = szOID_PKIX_POLICY_QUALIFIER_CPS;
	certPolicyQualifier.Qualifier.cbData = dwSize;
	certPolicyQualifier.Qualifier.pbData = pbCPSNotice;
	if ( (!CryptEncodeObject(X509_ASN_ENCODING, X509_CERT_POLICIES, (LPVOID)&certPolicyInfoArray, NULL, &dwSize))
		|| ((pbPolicyInfo = (BYTE*)malloc(dwSize)) == NULL)
		|| (!CryptEncodeObject(X509_ASN_ENCODING, X509_CERT_POLICIES, (LPVOID)&certPolicyInfoArray, pbPolicyInfo, &dwSize)) ) {
		oprintf("could not setup Certificate Policies: %s", winpki_error_str(0));
		goto out;
	}
	certExtension[2].pszObjId = szOID_CERT_POLICIES;
	certExtension[2].fCritical = FALSE;
	certExtension[2].Value.cbData = dwSize;
	certExtension[2].Value.pbData = pbPolicyInfo;

	certExtensionsArray.cExtension = ARRAYSIZE(certExtension);
	certExtensionsArray.rgExtension = certExtension;
	oprintf("set Enhanced Key Usage, URL and CPS");

	if (CryptAcquireContextW(&hCSP, wszKeyContainer, NULL, PROV_RSA_FULL, CRYPT_MACHINE_KEYSET|CRYPT_SILENT)) {
		oprintf("acquired existing key container");
	} else if ( (GetLastError() == NTE_BAD_KEYSET)
			 && (CryptAcquireContextW(&hCSP, wszKeyContainer, NULL, PROV_RSA_FULL, CRYPT_NEWKEYSET|CRYPT_MACHINE_KEYSET|CRYPT_SILENT)) ) {
		oprintf("created new key container");
	} else {
		oprintf("could not obtain a key container: %s", winpki_error_str(0));
		goto out;
	}

	// Generate key pair using RSA 4096
	// (Key_size <<16) because key size is in upper 16 bits
	if (!CryptGenKey(hCSP, AT_SIGNATURE, (4096U<<16) | CRYPT_EXPORTABLE, &hKey)) {
		oprintf("could not generate keypair: %s", winpki_error_str(0));
		goto out;
	}
	oprintf("generated new keypair");

	// Set the subject
	if ( (!CertStrToNameA(X509_ASN_ENCODING, szCertSubject, CERT_X500_NAME_STR, NULL, NULL, &SubjectIssuerBlob.cbData, NULL))
	  || ((SubjectIssuerBlob.pbData = (BYTE*)malloc(SubjectIssuerBlob.cbData)) == NULL)
	  || (!CertStrToNameA(X509_ASN_ENCODING, szCertSubject, CERT_X500_NAME_STR, NULL, SubjectIssuerBlob.pbData, &SubjectIssuerBlob.cbData, NULL)) ) {
		oprintf("could not encode subject name for self signed cert: %s", winpki_error_str(0));
		goto out;
	}

	// Prepare key provider structure for self-signed certificate
	memset(&KeyProvInfo, 0, sizeof(KeyProvInfo));
	KeyProvInfo.pwszContainerName = wszKeyContainer;
	KeyProvInfo.pwszProvName = NULL;
	KeyProvInfo.dwProvType = PROV_RSA_FULL;
	KeyProvInfo.dwFlags = CRYPT_MACHINE_KEYSET;
	KeyProvInfo.cProvParam = 0;
	KeyProvInfo.rgProvParam = NULL;
	KeyProvInfo.dwKeySpec = AT_SIGNATURE;

	// Prepare algorithm structure for self-signed certificate
	memset(&SignatureAlgorithm, 0, sizeof(SignatureAlgorithm));

	// Windows 7 does not properly support SHA256 and may show a "Trusted Publisher" dialog unless SHA1 is used
	SignatureAlgorithm.pszObjId = szOID_RSA_SHA1RSA;

	// Create self-signed certificate
	pCertContext = CertCreateSelfSignCertificate((ULONG_PTR)NULL,
		&SubjectIssuerBlob, 0, &KeyProvInfo, &SignatureAlgorithm, NULL, &sExpirationDate, &certExtensionsArray);
	if (pCertContext == NULL) {
		oprintf("could not create self signed certificate: %s", winpki_error_str(0));
		goto out;
	}
	oprintf("created new self-signed certificate '%s'", szCertSubject);

out:
	free(pbEnhKeyUsage);
	free(pbAltNameInfo);
	free(pbCPSNotice);
	free(pbPolicyInfo);
	free(SubjectIssuerBlob.pbData);
	if (hKey)
		CryptDestroyKey(hKey);
	if (hCSP)
		CryptReleaseContext(hCSP, 0);
	return pCertContext;
}

/*
 * Opens a file and computes the SHA1 Authenticode Hash
 */
static BOOL CalcHash(BYTE* pbHash, LPCWSTR wszFilePath)
{
	BOOL r = FALSE;
	HANDLE hFile = NULL;
	DWORD cbHash = SHA1_HASH_LENGTH;

	// Compute the SHA1 hash
	hFile = CreateFileW(wszFilePath, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
	if (hFile == INVALID_HANDLE_VALUE) goto out;
	if ( (!CryptCATAdminCalcHashFromFileHandle(hFile, &cbHash, pbHash, 0)) ) goto out;
	r = TRUE;

out:
	if (hFile)
		CloseHandle(hFile);
	return r;
}

/*
 * Add a new member to a cat file, containing the hash for the relevant file
 */
static BOOL AddFileHash(HANDLE hCat, LPWSTR wszFileName, BYTE* pbFileHash)
{
	const GUID inf_guid = {0xDE351A42, 0x8E59, 0x11D0, {0x8C, 0x47, 0x00, 0xC0, 0x4F, 0xC2, 0x95, 0xEE}};
	const GUID pe_guid = {0xC689AAB8, 0x8E78, 0x11D0, {0x8C, 0x47, 0x00, 0xC0, 0x4F, 0xC2, 0x95, 0xEE}};
	const BYTE fImageData = 0xA0;		// Flags used for the SPC_PE_IMAGE_DATA "<<<Obsolete>>>" link
	LPCWSTR wszOSAttr = L"2:5.1,2:5.2,2:6.0,2:6.1";

	BOOL bPEType = TRUE;
	CRYPTCATMEMBER* pCatMember = NULL;
	SIP_INDIRECT_DATA sSIPData;
	SPC_LINK sSPCLink;
	SPC_PE_IMAGE_DATA sSPCImageData;
	WCHAR wszHash[2*SHA1_HASH_LENGTH+1];
	LPCWSTR wszExt;
	BYTE pbEncoded[64];
	DWORD cbEncoded;
	int i;
	BOOL r= FALSE;

	// Create the required UTF-16 strings
	for (i=0; i<SHA1_HASH_LENGTH; i++) {
		StringCchPrintfW(&wszHash[2*i], 3, L"%02X", pbFileHash[i]);
	}
	_wcslwr_s(wszFileName, wcslen(wszFileName)+1);	// All cat filenames seem to be lowercases

	// Set the PE or CAB/INF type according to the extension
    wszExt = PathFindExtensionW(wszFileName);
	if ( CompareStringOrdinal(wszExt, -1, L".dll", -1, TRUE) == CSTR_EQUAL
        || CompareStringOrdinal(wszExt, -1, L".sys", -1, TRUE) == CSTR_EQUAL
        || CompareStringOrdinal(wszExt, -1, L".exe", -1, TRUE) == CSTR_EQUAL) {
		oprintf("'%S': PE type", wszFileName);
	} else if (CompareStringOrdinal(wszExt, -1, L".inf", -1, TRUE) == CSTR_EQUAL) {
		oprintf("'%S': INF type", wszFileName);
		bPEType = FALSE;
	} else {
		oprintf("unhandled file type: '%S' - ignoring", wszFileName);
		goto out;
	}

	// An "<<<Obsolete>>>" Authenticode link must be populated for each entry
	sSPCLink.dwLinkChoice = SPC_FILE_LINK_CHOICE;
	sSPCLink.pwszUrl = L"<<<Obsolete>>>";
	cbEncoded = sizeof(pbEncoded);
	// PE and INF encode the link differently
	if (bPEType) {
		sSPCImageData.Flags.cbData = 1;
		sSPCImageData.Flags.cUnusedBits = 0;
		sSPCImageData.Flags.pbData = (BYTE*)&fImageData;
		sSPCImageData.pFile = &sSPCLink;
		if (!CryptEncodeObject(X509_ASN_ENCODING, SPC_PE_IMAGE_DATA_OBJID, &sSPCImageData, pbEncoded, &cbEncoded)) {
			oprintf("unable to encode SPC Image Data: %s", winpki_error_str(0));
			goto out;
		}
	} else {
		if (!CryptEncodeObject(X509_ASN_ENCODING, SPC_CAB_DATA_OBJID, &sSPCLink, pbEncoded, &cbEncoded)) {
			oprintf("unable to encode SPC Image Data: %s", winpki_error_str(0));
			goto out;
		}
	}

	// Populate the SHA1 Hash OID
	sSIPData.Data.pszObjId = (bPEType)?SPC_PE_IMAGE_DATA_OBJID:SPC_CAB_DATA_OBJID;
	sSIPData.Data.Value.cbData = cbEncoded;
	sSIPData.Data.Value.pbData = pbEncoded;
	sSIPData.DigestAlgorithm.pszObjId = szOID_OIWSEC_sha1;
	sSIPData.DigestAlgorithm.Parameters.cbData = 0;
	sSIPData.Digest.cbData = SHA1_HASH_LENGTH;
	sSIPData.Digest.pbData = pbFileHash;

	// Create the new member
	if ((pCatMember = CryptCATPutMemberInfo(hCat, NULL, wszHash, (GUID*)((bPEType)?&pe_guid:&inf_guid),
		0x200, sizeof(sSIPData), (BYTE*)&sSIPData)) == NULL) {
		oprintf("unable to create cat entry for file '%S': %s", wszFileName, winpki_error_str(0));
		goto out;
	}

	// Add the "File" and "OSAttr" attributes to the newly created member
	if ( (CryptCATPutAttrInfo(hCat, pCatMember, L"File",
		  CRYPTCAT_ATTR_AUTHENTICATED|CRYPTCAT_ATTR_NAMEASCII|CRYPTCAT_ATTR_DATAASCII,
		  2*((DWORD)wcslen(wszFileName)+1), (BYTE*)wszFileName) == NULL)
	  || (CryptCATPutAttrInfo(hCat, pCatMember, L"OSAttr",
		  CRYPTCAT_ATTR_AUTHENTICATED|CRYPTCAT_ATTR_NAMEASCII|CRYPTCAT_ATTR_DATAASCII,
		  2*((DWORD)wcslen(wszOSAttr)+1), (BYTE*)wszOSAttr) == NULL) ) {
		oprintf("unable to create attributes for file '%S': %s", wszFileName, winpki_error_str(0));
		goto out;
	}
	r = TRUE;

out:
	return r;
}

/*
 * Add a certificate, identified by its pCertContext, to the system store 'szStoreName'
 */
BOOL AddCertToStore(PCCERT_CONTEXT pCertContext, LPCSTR szStoreName)
{
	HCERTSTORE hSystemStore = NULL;
	CRYPT_DATA_BLOB qvideoNameBlob = {14, (BYTE*)L"qvideo"};
	BOOL r = FALSE;

	hSystemStore = CertOpenStore(CERT_STORE_PROV_SYSTEM_A, X509_ASN_ENCODING,
		0, CERT_SYSTEM_STORE_LOCAL_MACHINE, szStoreName);
	if (hSystemStore == NULL) {
		oprintf("failed to open system store '%s': %s", szStoreName, winpki_error_str(0));
		goto out;
	}

	if (!CertSetCertificateContextProperty(pCertContext, CERT_FRIENDLY_NAME_PROP_ID, 0, &qvideoNameBlob)) {
		oprintf("coud not set friendly name: %s", winpki_error_str(0));
		goto out;
	}

	if (!CertAddCertificateContextToStore(hSystemStore, pCertContext, CERT_STORE_ADD_REPLACE_EXISTING, NULL)) {
		oprintf("failed to add certificate to system store '%s': %s", szStoreName, winpki_error_str(0));
		goto out;
	}
	r = TRUE;

out:
	if (hSystemStore != NULL)
		CertCloseStore(hSystemStore, 0);
	return r;
}

/*
 * Path and directory manipulation
 */
static void __inline HandleSeparators(LPWSTR wszPath)
{
	size_t i;
	if (wszPath == NULL) return;
	for (i=0; i<wcslen(wszPath); i++) {
		if (wszPath[i] == L'/') {
			wszPath[i] = L'\\';
		}
	}
}

static BOOL GetFullPath(LPCWSTR wszSrc, LPWSTR wszDst, DWORD nDstSize)
{
	DWORD r;
	LPWSTR wszSrcCopy = NULL;
    size_t nSrcSize;

	if ((wszSrc == NULL) || (wszDst == NULL) || (nDstSize == 0)) {
		return FALSE;
	}
    nSrcSize = wcslen(wszSrc) + 1;
	if ((wszSrcCopy = (LPWSTR)malloc(sizeof(*wszSrc) * nSrcSize)) == NULL) return 1;
    StringCchCopy(wszSrcCopy, nSrcSize, wszSrc);
	HandleSeparators(wszSrcCopy);
	r = GetFullPathNameW(wszSrcCopy, nDstSize, wszDst, NULL);
	free(wszSrcCopy);
	if ((r != 0) && (r <= nDstSize)) {
		return TRUE;
	}
	fprintf(stderr, "Unable to get full path for '%S'.\n", wszSrc);
	return FALSE;
}

// Modified from http://www.zemris.fer.hr/predmeti/os1/misc/Unix2Win.htm
static void ScanDirAndHash(HANDLE hCat, LPCWSTR wszInitialDir, LPCWSTR wszDirName, LPCWSTR* wszFileList, DWORD cFileList)
{
	WCHAR wszSubDir[MAX_PATH+1];
	WCHAR wszFilePath[MAX_PATH];
	WCHAR wszDir[MAX_PATH+1];
	HANDLE hList;
	WIN32_FIND_DATAW FileData;
	DWORD i;
	BYTE pbHash[SHA1_HASH_LENGTH];

	// Get the proper directory path
    if (FAILED(StringCbPrintfW(wszDir, sizeof(wszDir), L"%s%c%s", wszInitialDir, L'\\', wszDirName))) {
		oprintf("path overflow");
		return;
	}

	// Get the first file
	StringCbCat(wszDir, sizeof(wszDir), L"\\*");
	hList = FindFirstFileW(wszDir, &FileData);
	if (hList == INVALID_HANDLE_VALUE) return;

	// Traverse through the directory structure
	do {
		// Check the object is a directory or not
		if (FileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
			if ( (CompareStringOrdinal(FileData.cFileName, -1, L".", -1, FALSE) != CSTR_EQUAL)
			  && (CompareStringOrdinal(FileData.cFileName, -1, L"..", -1, FALSE) != CSTR_EQUAL)) {
				// Get the full path for sub directory
                if (FAILED(StringCbPrintfW(wszSubDir, sizeof(wszSubDir),
                                L"%s%c%s", wszDirName, L'\\', FileData.cFileName))) {
					oprintf("path overflow");
					FindClose(hList);
					return;
                }
				ScanDirAndHash(hCat, wszInitialDir, wszSubDir, wszFileList, cFileList);
			}
		} else {
			for (i=0; i<cFileList; i++) {
				if (CompareStringOrdinal(FileData.cFileName, -1, wszFileList[i], -1, TRUE) == CSTR_EQUAL) {
					if (FAILED(StringCbPrintfW(wszFilePath, sizeof(wszFilePath),
                            L"%s%s%c%s", wszInitialDir, wszDirName, L'\\', FileData.cFileName))) {
                        oprintf("path overflow");
                        FindClose(hList);
                        return;
                    }
					// TODO: check return value
					if ( (CalcHash(pbHash, wszFilePath)) && 
                            AddFileHash(hCat, FileData.cFileName, pbHash) ) {
						oprintf("added hash for '%S'",  wszFilePath);
					} else {
						oprintf("could not add hash for '%S' - ignored", wszFilePath);
					}
					break;
				}
			}
		}
	}
	while ( FindNextFileW(hList, &FileData) || (GetLastError() != ERROR_NO_MORE_FILES) );
	FindClose(hList);
}


/*
 * Create a cat file for driver package signing, and add any listed matching file found in the
 * wszSearchDir directory
 */
BOOL CreateCat(LPWSTR wszCatPath, LPCWSTR wszHWID, LPCWSTR wszSearchDir, LPCWSTR* wszFileList, DWORD cFileList)
{
	HCRYPTPROV hProv = 0;
	HANDLE hCat = NULL;
	BOOL r = FALSE;
	DWORD i;
	// From the inf2cat /os parameter - doesn't seem to be used by the OS though...
	LPCWSTR wszOS = L"7_X86,7_X64,8_X86,8_X64,8_ARM,10_X86,10_X64,10_ARM";
	LPWSTR * wszLocalFileList;
    WCHAR wszInitialDir[MAX_PATH];

	if (!CryptAcquireContextW(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
		oprintf("unable to acquire crypt context for cat creation");
		goto out;
	}
	hCat= CryptCATOpen(wszCatPath, CRYPTCAT_OPEN_CREATENEW, hProv, 0, 0);
	if (hCat == INVALID_HANDLE_VALUE) {
		oprintf("unable to create file '%S': %s", wszCatPath, winpki_error_str(0));
		goto out;
	}

	// Setup the general Cat attributes
	if (CryptCATPutCatAttrInfo(hCat, L"HWID1", CRYPTCAT_ATTR_AUTHENTICATED|CRYPTCAT_ATTR_NAMEASCII|CRYPTCAT_ATTR_DATAASCII,
		2*((DWORD)wcslen(wszHWID)+1), (BYTE*)wszHWID) ==  NULL) {
		oprintf("failed to set HWID1 cat attribute: %s", winpki_error_str(0));
		goto out;
	}
	if (CryptCATPutCatAttrInfo(hCat, L"OS", CRYPTCAT_ATTR_AUTHENTICATED|CRYPTCAT_ATTR_NAMEASCII|CRYPTCAT_ATTR_DATAASCII,
		2*((DWORD)wcslen(wszOS)+1), (BYTE*)wszOS) == NULL) {
		oprintf("failed to set OS cat attribute: %s", winpki_error_str(0));
		goto out;
	}

	// Setup the hash file members
	if (!GetFullPath(wszSearchDir, wszInitialDir, MAX_PATH)) {
		goto out;
	}
	// Make sure the list entries are all lowercase
	wszLocalFileList = (LPWSTR *)malloc(cFileList*sizeof(LPWSTR));
	if (wszLocalFileList == NULL) {
		oprintf("unable allocate local file list");
		goto out;
	}
	for (i=0; i<cFileList; i++){
		wszLocalFileList[i] = _wcsdup(wszFileList[i]);
		if (wszLocalFileList[i] == NULL)
			oprintf("'%S' could not be duplicated and will be ignored", wszFileList[i]);
		else
			_wcslwr_s(wszLocalFileList[i], wcslen(wszLocalFileList[i])+1);
	}
	ScanDirAndHash(hCat, wszInitialDir, L"", wszLocalFileList, cFileList);
	for (i=0; i<cFileList; i++){
		free(wszLocalFileList[i]);
	}
	free(wszLocalFileList);
	// The cat needs to be sorted before being saved
	if (!CryptCATPersistStore(hCat)) {
		oprintf("unable to sort file: %s",  winpki_error_str(0));
		goto out;
	}
	oprintf("successfully created file '%S'", wszCatPath);
	r = TRUE;

out:
	if (hProv)
		(CryptReleaseContext(hProv, 0));
	if (hCat)
		CryptCATClose(hCat);
	return r;
}

/*
 * Delete the private key associated with a specific cert
 */
BOOL DeletePrivateKey(PCCERT_CONTEXT pCertContext)
{
	LPWSTR wszKeyContainer = KEY_CONTAINER;
	HCRYPTPROV hCSP = 0;
	DWORD dwKeySpec;
	BOOL bFreeCSP = FALSE, r = FALSE;
	HCERTSTORE hSystemStore;
	LPCSTR szStoresToUpdate[2] = { "Root", "TrustedPublisher" };
	CRYPT_DATA_BLOB qvideoNameBlob = {14, (BYTE*)L"qvideo"};
	PCCERT_CONTEXT pCertContextUpdate = NULL;
	int i;

	if (!CryptAcquireCertificatePrivateKey(pCertContext, CRYPT_ACQUIRE_SILENT_FLAG, NULL, &hCSP, &dwKeySpec, &bFreeCSP)) {
		oprintf("error getting CSP: %s", winpki_error_str(0));
		goto out;
	}

	if (!CryptAcquireContextW(&hCSP, wszKeyContainer, NULL, PROV_RSA_FULL, CRYPT_MACHINE_KEYSET|CRYPT_SILENT|CRYPT_DELETEKEYSET)) {
		oprintf("failed to delete private key: %s", winpki_error_str(0));
	}

	// This is optional, but unless we reimport the cert data after having deleted the key
	// end users will still see a "You have a private key that corresponds to this certificate" message.
	for (i=0; i<ARRAYSIZE(szStoresToUpdate); i++)
	{
		hSystemStore = CertOpenStore(CERT_STORE_PROV_SYSTEM_A, X509_ASN_ENCODING,
			0, CERT_SYSTEM_STORE_LOCAL_MACHINE, szStoresToUpdate[i]);
		if (hSystemStore == NULL) continue;

		if ( (CertAddEncodedCertificateToStore(hSystemStore, X509_ASN_ENCODING, pCertContext->pbCertEncoded,
			pCertContext->cbCertEncoded, CERT_STORE_ADD_REPLACE_EXISTING, &pCertContextUpdate)) && (pCertContextUpdate != NULL) ) {
			// The friendly name is lost in this operation - restore it
			if (!CertSetCertificateContextProperty(pCertContextUpdate, CERT_FRIENDLY_NAME_PROP_ID, 0, &qvideoNameBlob)) {
				oprintf("coud not set friendly name: %s", winpki_error_str(0));
			}
			CertFreeCertificateContext(pCertContextUpdate);
		} else {
			oprintf("failed to update '%s': %s", szStoresToUpdate[i], winpki_error_str(0));
		}
		CertCloseStore(hSystemStore, 0);
	}

	r= TRUE;

out:
	if ((bFreeCSP) && (hCSP)) {
		CryptReleaseContext(hCSP, 0);
	}
	return r;
}

/*
 * Digitally sign a file and make it system-trusted by:
 * - creating a self signed certificate for code signing
 * - adding this certificate to both the Root and TrustedPublisher system stores
 * - signing the file provided
 * - deleting the self signed certificate private key so that it cannot be reused
 */
BOOL SelfSignFile(LPCWSTR wszFileName, LPCSTR szCertSubject)
{

	BOOL r = FALSE;
	HRESULT hResult = S_OK;
	PCCERT_CONTEXT pCertContext = NULL;
	DWORD dwIndex;
	SIGNER_FILE_INFO signerFileInfo;
	SIGNER_SUBJECT_INFO signerSubjectInfo;
	SIGNER_CERT_STORE_INFO signerCertStoreInfo;
	SIGNER_CERT signerCert;
	SIGNER_SIGNATURE_INFO signerSignatureInfo;
	PSIGNER_CONTEXT pSignerContext = NULL;
	CRYPT_ATTRIBUTES cryptAttributesArray;
	CRYPT_ATTRIBUTE cryptAttribute[2];
	CRYPT_INTEGER_BLOB oidSpOpusInfoBlob, oidStatementTypeBlob;
	BYTE pbOidSpOpusInfo[] = SP_OPUS_INFO_DATA;
	BYTE pbOidStatementType[] = STATEMENT_TYPE_DATA;

	// Delete any previous certificate with the same subject
	RemoveCertFromStore(szCertSubject, "Root");
	RemoveCertFromStore(szCertSubject, "TrustedPublisher");

	pCertContext = CreateSelfSignedCert(szCertSubject);
	if (pCertContext == NULL) {
		goto out;
	}
	oprintf("successfully created certificate '%s'", szCertSubject);
	if ( (!AddCertToStore(pCertContext, "Root"))
	  || (!AddCertToStore(pCertContext, "TrustedPublisher")) ) {
		goto out;
	}
	oprintf("added certificate '%s' to 'Root' and 'TrustedPublisher' stores", szCertSubject);

	// Setup SIGNER_FILE_INFO struct
	signerFileInfo.cbSize = sizeof(SIGNER_FILE_INFO);
	signerFileInfo.pwszFileName = wszFileName;
	signerFileInfo.hFile = NULL;

	// Prepare SIGNER_SUBJECT_INFO struct
	signerSubjectInfo.cbSize = sizeof(SIGNER_SUBJECT_INFO);
	dwIndex = 0;
	signerSubjectInfo.pdwIndex = &dwIndex;
	signerSubjectInfo.dwSubjectChoice = SIGNER_SUBJECT_FILE;
	signerSubjectInfo.pSignerFileInfo = &signerFileInfo;

	// Prepare SIGNER_CERT_STORE_INFO struct
	signerCertStoreInfo.cbSize = sizeof(SIGNER_CERT_STORE_INFO);
	signerCertStoreInfo.pSigningCert = pCertContext;
	signerCertStoreInfo.dwCertPolicy = SIGNER_CERT_POLICY_CHAIN;
	signerCertStoreInfo.hCertStore = NULL;

	// Prepare SIGNER_CERT struct
	signerCert.cbSize = sizeof(SIGNER_CERT);
	signerCert.dwCertChoice = SIGNER_CERT_STORE;
	signerCert.pCertStoreInfo = &signerCertStoreInfo;
	signerCert.hwnd = NULL;

	// Prepare the additional Authenticode OIDs
	oidSpOpusInfoBlob.cbData = sizeof(pbOidSpOpusInfo);
	oidSpOpusInfoBlob.pbData = pbOidSpOpusInfo;
	oidStatementTypeBlob.cbData = sizeof(pbOidStatementType);
	oidStatementTypeBlob.pbData = pbOidStatementType;
	cryptAttribute[0].cValue = 1;
	cryptAttribute[0].rgValue = &oidSpOpusInfoBlob;
	cryptAttribute[0].pszObjId = "1.3.6.1.4.1.311.2.1.12"; // SPC_SP_OPUS_INFO_OBJID in wintrust.h
	cryptAttribute[1].cValue = 1;
	cryptAttribute[1].rgValue = &oidStatementTypeBlob;
	cryptAttribute[1].pszObjId = "1.3.6.1.4.1.311.2.1.11"; // SPC_STATEMENT_TYPE_OBJID in wintrust.h
	cryptAttributesArray.cAttr = 2;
	cryptAttributesArray.rgAttr = cryptAttribute;

	// Prepare SIGNER_SIGNATURE_INFO struct
	signerSignatureInfo.cbSize = sizeof(SIGNER_SIGNATURE_INFO);
	signerSignatureInfo.algidHash = CALG_SHA1;
	signerSignatureInfo.dwAttrChoice = SIGNER_NO_ATTR;
	signerSignatureInfo.pAttrAuthcode = NULL;
	signerSignatureInfo.psAuthenticated = &cryptAttributesArray;
	signerSignatureInfo.psUnauthenticated = NULL;

	// Sign file with cert
	hResult = SignerSignEx(0, &signerSubjectInfo, &signerCert, &signerSignatureInfo, NULL, NULL, NULL, NULL, &pSignerContext);
	if (hResult != S_OK) {
		oprintf("SignerSignEx failed. hResult #%X, error %s", hResult, winpki_error_str(0));
		goto out;
	}
	r = TRUE;
	oprintf("successfully signed file '%S'", wszFileName);

	// Clean up
out:
	/*
	 * Because we installed our certificate as a Root CA as well as a Trusted Publisher
	 * we *MUST* ensure that the private key is destroyed, so that it cannot be reused
	 * by an attacker to self sign a malicious applications.
	 */
	if ((pCertContext != NULL) && (DeletePrivateKey(pCertContext))) {
		oprintf("successfully deleted private key");
	}
	if (pSignerContext != NULL)
		SignerFreeSignerContext(pSignerContext);
	if (pCertContext != NULL)
		CertFreeCertificateContext(pCertContext);
	return r;
}

void usage(void)
{
        printf("\n");
        printf("-p, --path <dir>           set the qvideo directory\n");
        printf("-c, --cert <certpath>      install certificate <certpath> as a trusted publisher\n");
        printf("-v, --verbose              verbose mode\n");
        printf("\n");
}

#define DEFAULT_DIR L"C:\\Program Files\\Invisible Things Lab\\Qubes Tools\\Drivers\\qvideo"

int __cdecl wmain(int argc, WCHAR* argv[])
{
	static WCHAR* hw_id = L"itl_qubesvideo"; // keep it lowercase for cat file
	static char* cert_subject = "CN=QUBES-AUTOGENERATED-CERT";
	static const WCHAR* cat_list[3] = {L"qvmini.sys", L"qvideo.inf", L"qvgdi.dll"};
	static WCHAR* cat_filename = L"qvideo.cat";
	WCHAR* drv_path = DEFAULT_DIR;
        WCHAR cat_path[MAX_PATH];
	WCHAR opt;

    	while ((opt = getopt(argc, argv, TEXT("p:v"))) != 0)
    	{
        	switch (opt) {
                case 'p': 
			drv_path = optarg;
                        break;
                case 'v':
                        opt_silent = 0;
                        break;
                default:
                        usage();
                        exit(0);
                }
        }
	StringCbCopyW(cat_path, sizeof(cat_path), drv_path);
        StringCbCatW(cat_path, sizeof(cat_path), L"\\");
        StringCbCatW(cat_path, sizeof(cat_path), "qvmini.sys");
        SelfSignFile(cat_path, cert_subject);

        StringCbCopyW(cat_path, sizeof(cat_path), drv_path);
        StringCbCatW(cat_path, sizeof(cat_path), L"\\");
        StringCbCatW(cat_path, sizeof(cat_path), "qvgdi.dll");
        SelfSignFile(cat_path, cert_subject);

	StringCbCopyW(cat_path, sizeof(cat_path), drv_path);
        StringCbCatW(cat_path, sizeof(cat_path), L"\\");
        StringCbCatW(cat_path, sizeof(cat_path), cat_filename);

        if (!CreateCat(cat_path, hw_id, drv_path, cat_list, 3))
        	oprintf("could not create cat file");
        else if (!SelfSignFile(cat_path, cert_subject))
                oprintf("could not sign cat file");
         
	return 0;
}

