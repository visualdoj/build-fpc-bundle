default : aggregate ;

.PHONY : aggregate ;

ifeq ($(OS),Windows_NT)
  CP := $(CURDIR)\bin\i386-win32\cp.exe
  CAT := $(CURDIR)\bin\i386-win32\cat.exe
  TAR := tar.exe
  MV := $(CURDIR)\bin\i386-win32\mv.exe
  ECHO := $(CURDIR)\bin\i386-win32\echo.exe
else
  CP := cp
  CAT := cat
  TAR := tar
  MV := mv
  ECHO := echo
endif

ifneq ($(BUNDLE_NAME),)
CROSS_ARTIFACTS:=$(wildcard $(BUNDLE_NAME)-cross-*.tar.gz)
CROSS_UNPACKED:=$(CROSS_ARTIFACTS:%.tar.gz=%-unpacked)
CROSS_LISTS   :=$(CROSS_ARTIFACTS:%.tar.gz=%-unpacked/info/cross-list.txt)
CROSS_CFG     :=$(CROSS_ARTIFACTS:%.tar.gz=%-unpacked/fpc.cfg)

aggregate : $(BUNDLE_NAME)-cross.tar.gz ;
$(BUNDLE_NAME)-cross.tar.gz : bundle-cross
	$(TAR) -czvf $@ $</*
bundle-cross : $(CROSS_UNPACKED)
	$(TAR) -zxvf $(BUNDLE_NAME).tar.gz/$(BUNDLE_NAME).tar.gz
	mv bundle $@
	@$(ECHO) >$@/info/cross-list.txt
	$(CAT) $(CROSS_LISTS) >>$@/info/cross-list.txt
	$(CAT) $(CROSS_CFG)   >>$@/fpc.cfg
$(BUNDLE_NAME)-%-unpacked : $(BUNDLE_NAME)-%.tar.gz config
	$(TAR) -zxvf $</$<
	$(MV) bundle-cross $@
config :
	$(ECHO) $(CROSS_ARTIFACTS)
	$(ECHO) $(CROSS_UNPACKED)
	$(ECHO) $(CROSS_LISTS)
	$(ECHO) $(CROSS_CFG)
else
aggregate :
	@$(ECHO) You should specify BUNDLE_NAME to run aggregate
endif

