@echo off

bcdedit /set {current} recoveryenabled no

bcdedit /set {current} bootstatuspolicy ignoreallfailures

sc config defragsvc start= disabled

sc config WSearch start= disabled

sc config fdPHost start= disabled

sc config PNRPsvc start= disabled

sc config p2psvc start= disabled

sc config p2pimsvc start= disabled

sc config xenlite start= disabled
