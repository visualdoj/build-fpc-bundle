default : aggregate ;

.PHONY : aggregate ;

ifeq ($(OS),Windows_NT)
  WINDOWS_TOOLS := $(CURDIR)\bin\i386-win32
  CP    := $(WINDOWS_TOOLS)\cp.exe
  CAT   := $(WINDOWS_TOOLS)\cat.exe
  TAR   := tar.exe
  MV    := $(WINDOWS_TOOLS)\mv.exe
  ECHO  := $(WINDOWS_TOOLS)\echo.exe
  PASS  := $(WINDOWS_TOOLS)\test.exe -z ""
  MKDIR := $(WINDOWS_TOOLS)\mkdir.exe
else
  CP    := cp
  CAT   := cat
  TAR   := tar
  MV    := mv
  ECHO  := echo
  PASS  := true
  MKDIR := mkdir
endif

ifneq ($(BUNDLE_NAME),)
CROSS_ARTIFACTS:=$(wildcard $(BUNDLE_NAME)-cross-*.tar.gz)
CROSS_UNPACKED:=$(CROSS_ARTIFACTS:%.tar.gz=%-unpacked)
CROSS_LISTS   :=$(CROSS_ARTIFACTS:%.tar.gz=%-unpacked/info/cross-list.txt)
CROSS_CFG     :=$(CROSS_ARTIFACTS:%.tar.gz=%-unpacked/fpc.cfg)
CROSS_BIN     :=$(CROSS_ARTIFACTS:%.tar.gz=%-unpacked/installed/bin/*)

  ifneq ($(OS),Windows_NT)
    CROSS_BIN += $(CROSS_ARTIFACTS:%.tar.gz=%-unpacked/installed/lib/fpc/*/ppcross*)
  endif

aggregate : $(BUNDLE_NAME)-cross.tar.gz ;
$(BUNDLE_NAME)-cross.tar.gz : bundle-cross
	cd $< && $(TAR) -czvf ../$@ *
bundle-cross : $(CROSS_UNPACKED)
	$(MKDIR) -p $@
	cd $@ && $(TAR) -zxvf ../$(BUNDLE_NAME).tar.gz/$(BUNDLE_NAME).tar.gz
	@$(ECHO) >$@/info/cross-list.txt
	$(CAT) $(CROSS_LISTS) >>$@/info/cross-list.txt
	$(CAT) $(CROSS_CFG)   >>$@/fpc.cfg
	$(CP) -f $(CROSS_BIN) $@/installed/bin/ || $(PASS)
$(BUNDLE_NAME)-%-unpacked : $(BUNDLE_NAME)-%.tar.gz config
	$(MKDIR) -p $@
	cd $@ && $(TAR) -zxvf ../$</$<
config :
	$(ECHO) $(CROSS_ARTIFACTS)
	$(ECHO) $(CROSS_UNPACKED)
	$(ECHO) $(CROSS_LISTS)
	$(ECHO) $(CROSS_CFG)
else
aggregate :
	@$(ECHO) You should specify BUNDLE_NAME to run aggregate
endif
