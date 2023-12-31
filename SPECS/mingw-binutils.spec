%global run_testsuite 1

Name:           mingw-binutils
Version:        2.30
Release:        3%{?dist}
Summary:        Cross-compiled version of binutils for Win32 and Win64 environments

License:        GPLv2+ and LGPLv2+ and GPLv3+ and LGPLv3+
Group:          Development/Libraries

URL:            http://www.gnu.org/software/binutils/
Source0:        http://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.bz2
#Source0:        http://www.kernel.org/pub/linux/devel/binutils/binutils-% {version}.tar.bz2

Patch0001: 0001-Remove-PROVIDE-qualifiers.patch

BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  texinfo
BuildRequires:  zlib-devel
BuildRequires:  mingw32-filesystem >= 102
BuildRequires:  mingw64-filesystem >= 102
%if %{run_testsuite}
BuildRequires:  dejagnu
BuildRequires:  sharutils
%endif
Provides:       bundled(libiberty)


%description
Cross compiled binutils (utilities like 'strip', 'as', 'ld') which
understand Windows executables and DLLs.

%package -n mingw-binutils-generic
Summary:        Utilities which are needed for both the Win32 and Win64 toolchains

%description -n mingw-binutils-generic
Utilities (like strip and objdump) which are needed for
both the Win32 and Win64 toolchains

%package -n mingw32-binutils
Summary:        Cross-compiled version of binutils for the Win32 environment
Requires:       mingw-binutils-generic = %{version}-%{release}

# NB: This must be left in.
Requires:       mingw32-filesystem >= 95

%description -n mingw32-binutils
Cross compiled binutils (utilities like 'strip', 'as', 'ld') which
understand Windows executables and DLLs.

%package -n mingw64-binutils
Summary:        Cross-compiled version of binutils for the Win64 environment
Requires:       mingw-binutils-generic = %{version}-%{release}

# NB: This must be left in.
Requires:       mingw64-filesystem >= 95

%description -n mingw64-binutils
Cross compiled binutils (utilities like 'strip', 'as', 'ld') which
understand Windows executables and DLLs.


%prep
%setup -q -n binutils-%{version}
%patch0001 -p1 -b .0001

%build
mkdir build_win32
pushd build_win32
CFLAGS="$RPM_OPT_FLAGS" \
../configure \
  --build=%_build --host=%_host \
  --target=%{mingw32_target} \
  --disable-nls \
  --with-sysroot=%{mingw32_sysroot} \
  --prefix=%{_prefix} \
  --bindir=%{_bindir} \
  --includedir=%{_includedir} \
  --libdir=%{_libdir} \
  --mandir=%{_mandir} \
  --infodir=%{_infodir}

make all %{?_smp_mflags}
popd

mkdir build_win64
pushd build_win64
CFLAGS="$RPM_OPT_FLAGS" \
../configure \
  --build=%_build --host=%_host \
  --target=%{mingw64_target} \
  --disable-nls \
  --with-sysroot=%{mingw64_sysroot} \
  --prefix=%{_prefix} \
  --bindir=%{_bindir} \
  --includedir=%{_includedir} \
  --libdir=%{_libdir} \
  --mandir=%{_mandir} \
  --infodir=%{_infodir}

make all %{?_smp_mflags}
popd

# Create multilib versions for the tools strip, objdump nm, and objcopy
mkdir build_multilib
pushd build_multilib
CFLAGS="$RPM_OPT_FLAGS" \
../configure \
  --build=%_build --host=%_host \
  --target=%{mingw64_target} \
  --enable-targets=%{mingw64_target},%{mingw32_target} \
  --disable-nls \
  --with-sysroot=%{mingw64_sysroot} \
  --prefix=%{_prefix} \
  --bindir=%{_bindir} \
  --includedir=%{_includedir} \
  --libdir=%{_libdir} \
  --mandir=%{_mandir} \
  --infodir=%{_infodir}

make %{?_smp_mflags}
popd


%check
%if !%{run_testsuite}
echo ====================TESTSUITE DISABLED=========================
%else
pushd build_win32
  make -k check < /dev/null || :
  echo ====================TESTING WIN32 =========================
  cat {gas/testsuite/gas,ld/ld,binutils/binutils}.sum
  echo ====================TESTING WIN32 END=====================
  for file in {gas/testsuite/gas,ld/ld,binutils/binutils}.{sum,log}
  do
    ln $file binutils-%{mingw32_target}-$(basename $file) || :
  done
  tar cjf binutils-%{mingw32_target}.tar.bz2 binutils-%{mingw32_target}-*.{sum,log}
  uuencode binutils-%{mingw32_target}.tar.bz2 binutils-%{mingw32_target}.tar.bz2
  rm -f binutils-%{mingw32_target}.tar.bz2 binutils-%{mingw32_target}-*.{sum,log}
popd

pushd build_win64
  make -k check < /dev/null || :
  echo ====================TESTING WIN64 =========================
  cat {gas/testsuite/gas,ld/ld,binutils/binutils}.sum
  echo ====================TESTING WIN64 END=====================
  for file in {gas/testsuite/gas,ld/ld,binutils/binutils}.{sum,log}
  do
    ln $file binutils-%{mingw64_target}-$(basename $file) || :
  done
  tar cjf binutils-%{mingw64_target}.tar.bz2 binutils-%{mingw64_target}-*.{sum,log}
  uuencode binutils-%{mingw64_target}.tar.bz2 binutils-%{mingw64_target}.tar.bz2
  rm -f binutils-%{mingw64_target}.tar.bz2 binutils-%{mingw64_target}-*.{sum,log}
popd
%endif


%install
%mingw_make_install DESTDIR=$RPM_BUILD_ROOT
make -C build_multilib DESTDIR=$RPM_BUILD_ROOT/multilib install

# These files conflict with ordinary binutils.
rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -f $RPM_BUILD_ROOT%{_libdir}/libiberty*

# Keep the multilib versions of the strip, objdump and objcopy commands
# We need these for the RPM integration as these tools must be able to
# both process win32 and win64 binaries
mv $RPM_BUILD_ROOT/multilib%{_bindir}/%{mingw64_strip} $RPM_BUILD_ROOT%{_bindir}/%{mingw_strip}
mv $RPM_BUILD_ROOT/multilib%{_bindir}/%{mingw64_objdump} $RPM_BUILD_ROOT%{_bindir}/%{mingw_objdump}
mv $RPM_BUILD_ROOT/multilib%{_bindir}/%{mingw64_objcopy} $RPM_BUILD_ROOT%{_bindir}/%{mingw_objcopy}
mv $RPM_BUILD_ROOT/multilib%{_bindir}/%{mingw64_nm} $RPM_BUILD_ROOT%{_bindir}/%{mingw_nm}
rm -rf $RPM_BUILD_ROOT/multilib


%files -n mingw-binutils-generic
%doc COPYING
%{_mandir}/man1/*
%{_bindir}/%{mingw_strip}
%{_bindir}/%{mingw_objdump}
%{_bindir}/%{mingw_objcopy}
%{_bindir}/%{mingw_nm}

%files -n mingw32-binutils
%{_bindir}/%{mingw32_target}-addr2line
%{_bindir}/%{mingw32_target}-ar
%{_bindir}/%{mingw32_target}-as
%{_bindir}/%{mingw32_target}-c++filt
%{_bindir}/%{mingw32_target}-dlltool
%{_bindir}/%{mingw32_target}-dllwrap
%{_bindir}/%{mingw32_target}-elfedit
%{_bindir}/%{mingw32_target}-gprof
%{_bindir}/%{mingw32_target}-ld
%{_bindir}/%{mingw32_target}-ld.bfd
%{_bindir}/%{mingw32_target}-nm
%{_bindir}/%{mingw32_target}-objcopy
%{_bindir}/%{mingw32_target}-objdump
%{_bindir}/%{mingw32_target}-ranlib
%{_bindir}/%{mingw32_target}-readelf
%{_bindir}/%{mingw32_target}-size
%{_bindir}/%{mingw32_target}-strings
%{_bindir}/%{mingw32_target}-strip
%{_bindir}/%{mingw32_target}-windmc
%{_bindir}/%{mingw32_target}-windres
%{_prefix}/%{mingw32_target}/bin/ar
%{_prefix}/%{mingw32_target}/bin/as
%{_prefix}/%{mingw32_target}/bin/dlltool
%{_prefix}/%{mingw32_target}/bin/ld
%{_prefix}/%{mingw32_target}/bin/ld.bfd
%{_prefix}/%{mingw32_target}/bin/nm
%{_prefix}/%{mingw32_target}/bin/objcopy
%{_prefix}/%{mingw32_target}/bin/objdump
%{_prefix}/%{mingw32_target}/bin/ranlib
%{_prefix}/%{mingw32_target}/bin/readelf
%{_prefix}/%{mingw32_target}/bin/strip
%{_prefix}/%{mingw32_target}/lib/ldscripts

%files -n mingw64-binutils
%{_bindir}/%{mingw64_target}-addr2line
%{_bindir}/%{mingw64_target}-ar
%{_bindir}/%{mingw64_target}-as
%{_bindir}/%{mingw64_target}-c++filt
%{_bindir}/%{mingw64_target}-dlltool
%{_bindir}/%{mingw64_target}-dllwrap
%{_bindir}/%{mingw64_target}-elfedit
%{_bindir}/%{mingw64_target}-gprof
%{_bindir}/%{mingw64_target}-ld
%{_bindir}/%{mingw64_target}-ld.bfd
%{_bindir}/%{mingw64_target}-nm
%{_bindir}/%{mingw64_target}-objcopy
%{_bindir}/%{mingw64_target}-objdump
%{_bindir}/%{mingw64_target}-ranlib
%{_bindir}/%{mingw64_target}-readelf
%{_bindir}/%{mingw64_target}-size
%{_bindir}/%{mingw64_target}-strings
%{_bindir}/%{mingw64_target}-strip
%{_bindir}/%{mingw64_target}-windmc
%{_bindir}/%{mingw64_target}-windres
%{_prefix}/%{mingw64_target}/bin/ar
%{_prefix}/%{mingw64_target}/bin/as
%{_prefix}/%{mingw64_target}/bin/dlltool
%{_prefix}/%{mingw64_target}/bin/ld
%{_prefix}/%{mingw64_target}/bin/ld.bfd
%{_prefix}/%{mingw64_target}/bin/nm
%{_prefix}/%{mingw64_target}/bin/objcopy
%{_prefix}/%{mingw64_target}/bin/objdump
%{_prefix}/%{mingw64_target}/bin/ranlib
%{_prefix}/%{mingw64_target}/bin/readelf
%{_prefix}/%{mingw64_target}/bin/strip
%{_prefix}/%{mingw64_target}/lib/ldscripts


%changelog
* Tue Dec 01 2020 Uri Lublin <uril@redhat.com> - 2.30-3
- rebuilt

* Thu Jun 11 2020 Uri Lublin <uril@redhat.com> - 2.30-2
- Remove PROVIDE() qualifiers from definition of __CTOR_LIST__ and __DTOR_LIST__
  Resolves: rhbz#1846152

* Wed Aug 22 2018 Victor Toso <victortoso@redhat.com> - 2.30-1
- Update to 2.30
- Related: rhbz#1615874

* Sun Oct 08 2017 Kalev Lember <klember@redhat.com> - 2.29.1-1
- Update to 2.29.1

* Tue Sep 19 2017 Sandro Mani <manisandro@gmail.com> - 2.29-4
- Rebuild for mingw-filesystem (for %%mingw_nm macro)

* Fri Aug 25 2017 Sandro Mani <manisandro@gmail.com> - 2.29-3
- Also build multilib version of nm

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.29-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Kalev Lember <klember@redhat.com> - 2.29-1
- Update to 2.29

* Mon Mar 06 2017 Kalev Lember <klember@redhat.com> - 2.28-1
- Update to 2.28

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.27-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Aug 10 2016 Kalev Lember <klember@redhat.com> - 2.27-1
- Update to 2.27

* Tue May 10 2016 Kalev Lember <klember@redhat.com> - 2.26-1
- Update to 2.26

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.25-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Dec 23 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.25-1
- Update to 2.25

* Tue Dec 23 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.24-5
- Fix CVE-2014-8501 (RHBZ #1162578 #1162583)
- Fix CVE-2014-8502 (RHBZ #1162602)
- Fix CVE-2014-8503 (RHBZ #1162612)
- Fix CVE-2014-8504 (RHBZ #1162626)
- Fix CVE-2014-8737 (RHBZ #1162660)
- Fix CVE-2014-8738 (RHBZ #1162673)

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.24-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.24-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 30 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.24-2
- Fix FTBFS against gcc 4.9

* Sat Jan 11 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.24-1
- Update to 2.24

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.23.52.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Apr  3 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.23.52.0.1-1
- Update to 2.23.52.0.1
- Fixes FTBFS against latest texinfo
- Resolve build failure on PPC

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.23.51.0.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Jan 22 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.23.51.0.5-3
- Backported patch to fix 'unexpected version string length' error in windres (RHBZ #902960)

* Tue Nov 27 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.23.51.0.5-2
- Added BR: zlib-devel to enable support for compressed debug sections

* Wed Nov 21 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.23.51.0.5-1
- Update to 2.23.51.0.5 release

* Mon Oct 15 2012 Jon Ciesla <limburgher@gmail.com> - 2.22.52.0.4-2
- Provides: bundled(libiberty)

* Wed Jul 18 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.22.52.0.4-1
- Update to 2.22.52.0.4 release

* Sat Jun  2 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.22.52.0.3-1
- Update to 2.22.52.0.3 release

* Sun Apr  8 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.22.52-4
- Cleaned up unneeded %%global tags

* Tue Mar  6 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.22.52-3
- Made the package compliant with the new MinGW packaging guidelines
- Added win64 support
- Added a mingw-binutils-generic package containing toolchain
  utilities which can be used by both the win32 and win64 toolchains
- Enable the testsuite
- Package the license
- Fix source URL

* Tue Mar  6 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.22.52-2
- Renamed the source package to mingw-binutils (RHBZ #673786)
- Use mingw macros without leading underscore

* Sat Feb 25 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.22.52-1
- Update to 2.22.52 20120225 snapshot
- Bump the BR/R: mingw32-filesystem to >= 95
- Rebuild using the i686-w64-mingw32 triplet
- Dropped some obsolete configure arguments
- Temporary provide mingw-strip, mingw-objdump and mingw-objcopy
  in preparation for win32+win64 support

* Tue Jan 10 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.22-1
- Update to 2.22
- Dropped unneeded RPM tags
- Use parallel make

* Tue May 10 2011 Kalev Lember <kalev@smartlink.ee> - 2.21-2
- Default to runtime pseudo reloc v2 now that mingw32-runtime 3.18 is in

* Thu Mar 17 2011 Kalev Lember <kalev@smartlink.ee> - 2.21-1
- Update to 2.21
- Added a patch to use runtime pseudo reloc v1 by default as the version of
  mingw32-runtime we have does not support v2.
- Don't own the /usr/i686-pc-mingw32/bin/ directory

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.20.51.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Sep  7 2010 Richard W.M. Jones <rjones@redhat.com> - 2.20.51.0.10-1
- Synchronize with Fedora native version (2.20.51.0.10).
- Note however that we are not using any Fedora patches.

* Thu May 13 2010 Kalev Lember <kalev@smartlink.ee> - 2.20.1-1
- Update to 2.20.1

* Wed Sep 16 2009 Kalev Lember <kalev@smartlink.ee> - 2.19.51.0.14-1
- Update to 2.19.51.0.14

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.19.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Mar 10 2009 Richard W.M. Jones <rjones@redhat.com> - 2.19.1-4
- Switch to using upstream (GNU) binutils 2.19.1.  It's exactly the
  same as the MinGW version now.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.19.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 20 2009 Richard W.M. Jones <rjones@redhat.com> - 2.19.1-2
- Rebuild for mingw32-gcc 4.4

* Tue Feb 10 2009 Richard W.M. Jones <rjones@redhat.com> - 2.19.1-1
- New upstream version 2.19.1.

* Mon Dec 15 2008 Richard W.M. Jones <rjones@redhat.com> - 2.19-1
- New upstream version 2.19.

* Sat Nov 29 2008 Richard W.M. Jones <rjones@redhat.com> - 2.18.50_20080109_2-10
- Must runtime-require mingw32-filesystem.

* Fri Nov 21 2008 Levente Farkas <lfarkas@lfarkas.org> - 2.18.50_20080109_2-9
- BR mingw32-filesystem >= 38

* Wed Sep 24 2008 Richard W.M. Jones <rjones@redhat.com> - 2.18.50_20080109_2-8
- Rename mingw -> mingw32.
- BR mingw32-filesystem >= 26.

* Thu Sep  4 2008 Richard W.M. Jones <rjones@redhat.com> - 2.18.50_20080109_2-7
- Use mingw-filesystem.

* Mon Jul  7 2008 Richard W.M. Jones <rjones@redhat.com> - 2.18.50_20080109_2-5
- Initial RPM release, largely based on earlier work from several sources.
