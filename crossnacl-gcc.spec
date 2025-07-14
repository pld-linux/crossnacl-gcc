#
# Conditional build:
%bcond_with	bootstrap	# build without NaCl newlib package dependency (without c++,objc packages)

%define		gitver	3960379
%define		rel	1
Summary:	Various compilers (C, C++) for NaCl
Summary(pl.UTF-8):	Różne kompilatory (C, C++) dla NaCl
Name:		crossnacl-gcc
Version:	4.4.3
Release:	13.git%{gitver}.%{rel}
License:	GPL v3+ and GPL v3+ with exceptions and GPL v2+ with exceptions
Group:		Development/Languages
Source0:	nacl-gcc-%{version}-git%{gitver}.tar.xz
# Source0-md5:	e72fed38d5b93e4505c1a05c69ab0796
Source1:	get-source.sh
Patch0:		gnu_inline-mismatch.patch
URL:		http://sourceware.org/gcc/
BuildRequires:	cloog-ppl-devel >= 0.15
BuildRequires:	crossnacl-binutils
BuildRequires:	elfutils-devel
BuildRequires:	gmp-c++-devel >= 4.1
BuildRequires:	gmp-devel >= 4.1
BuildRequires:	libstdc++-devel
BuildRequires:	mpfr-devel >= 2.3.2
BuildRequires:	perl-tools-pod
BuildRequires:	ppl-devel >= 0.10
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildConflicts:	cloog-isl-devel
%if %{without bootstrap}
BuildRequires:	crossnacl-newlib
%endif
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		x86_64-nacl
%define		archprefix	%{_prefix}/%{target}
%define		archbindir	%{archprefix}/bin
%define		archincludedir	%{archprefix}/include
%define		archlib32dir	%{archprefix}/lib32
%define		archlib64dir	%{archprefix}/lib64
%define		gccarchdir	%{_libdir}/gcc/%{target}
%define		gcclibdir	%{gccarchdir}/%{version}

%define		filterout_cpp	-D_FORTIFY_SOURCE=[0-9]+
%define		filterout_c	-Werror=format-security

%description
The gcc package contains the GNU Compiler Collection.

This package provides support for NaCl targets.

%description -l pl.UTF-8
Pakiet gcc zawiera zestaw kompilatorów GNU Compiler Collection.

Ten pakiet zapewnia obsługę platformy docelowej NaCl.

%package c++
Summary:	C++ support for crossnacl-gcc
Summary(pl.UTF-8):	Obsługa C++ dla crossnacl-gcc
Group:		Development/Languages
Requires:	%{name} = %{version}-%{release}

%description c++
This package adds C++ support to the GNU Compiler Collection for NaCl
targets.

%description c++ -l pl.UTF-8
Ten pakiet dodaje obsługę C++ do kompilatora gcc dla NaCl.

%package objc
Summary:	NaCl binary utility development utilities - objc
Summary(pl.UTF-8):	Zestaw narzędzi programistycznych NaCl - objc
Group:		Development/Languages
Requires:	%{name} = %{version}-%{release}

%description objc
This package contains objc compiler cross targeted to NaCl.

%description objc -l pl.UTF-8
Ten pakiet zawiera kompilator objc generujący kod dla NaCl.

%prep
%setup -q -n nacl-gcc-%{version}-git%{?gitver}
%patch -P0 -p1

%build
rm -rf obj-%{target}
install -d obj-%{target}
cd obj-%{target}

OPT_FLAGS="%{rpmcflags} -D_FILE_OFFSET_BITS=64 -fgnu89-inline"
OPT_FLAGS=$(echo "$OPT_FLAGS" | sed -e 's/-m64//g;s/-m32//g;s/-m31//g')
%ifarch %{ix86}
OPT_FLAGS=$(echo "$OPT_FLAGS" | sed -e 's/-march=i.86//g')
%endif
OPT_FLAGS=$(echo "$OPT_FLAGS" | sed -e 's/[[:blank:]]\+/ /g')

case "$OPT_FLAGS" in
*-fasynchronous-unwind-tables*)
	%{__sed} -i -e 's/-fno-exceptions /-fno-exceptions -fno-asynchronous-unwind-tables/' \
	../gcc/Makefile.in
;;
esac

GCC_DEFINES="-Dinhibit_libc -D__gthr_posix_h"
../configure \
	CC="%{__cc}" \
	CFLAGS="$OPT_FLAGS $GCC_DEFINES" \
	CXXFLAGS="$(echo $OPT_FLAGS | sed 's/ -Wall / /g')" \
	XCFLAGS="$OPT_FLAGS" \
	MAKEINFO=/bin/true \
	--prefix=%{_prefix} \
	--mandir=%{_mandir} \
	--infodir=%{_infodir} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libdir} \
	--enable-__cxa_atexit \
	--enable-checking=release \
	--disable-decimal-float \
	--enable-gnu-unique-object \
	--disable-libgcj \
	--disable-libgomp \
	--disable-libmudflap \
	--disable-libssp \
	--disable-libstdcxx-pch \
	--disable-libunwind-exceptions \
	--disable-ppl-version-check \
	--disable-shared \
	--with-cloog \
	--with-host-libstdcxx="-lstdc++ -lm" \
	--with-ppl \
	--with-system-zlib \
%if %{with bootstrap}
	CFLAGS_FOR_TARGET="-O2 -g" \
	CXXFLAGS_FOR_TARGET="-O2 -g" \
	--enable-languages="c" \
	--disable-threads \
	--without-headers \
%else
	CFLAGS_FOR_TARGET="-O2 -g -mtls-use-call -I/usr/x86_64-nacl/include/" \
	CXXFLAGS_FOR_TARGET="-O2 -g -mtls-use-call -I/usr/x86_64-nacl/include/" \
	--enable-languages="c,c++,objc" \
	--enable-threads=nacl \
	--enable-tls \
	--with-newlib \
%endif
	--target=%{target}

%{__make} \
	BOOT_CFLAGS="$OPT_FLAGS" \
%if %{with bootstrap}
	all-gcc all-target-libgcc
%else
	all
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C obj-%{target} \
%if %{with bootstrap}
	install-gcc install-target-libgcc \
%else
	install \
%endif
	DESTDIR=$RPM_BUILD_ROOT

# move fixed includes to proper place
%{__mv} $RPM_BUILD_ROOT%{gcclibdir}/include-fixed/{limits,syslimits}.h $RPM_BUILD_ROOT%{gcclibdir}/include
%{__rm} -r $RPM_BUILD_ROOT%{gcclibdir}/include-fixed
%{__rm} -r $RPM_BUILD_ROOT%{gcclibdir}/install-tools

# Delete supplemental files that would conflict with the core toolchain
%{__rm} -r $RPM_BUILD_ROOT%{_infodir}
%{__rm} -r $RPM_BUILD_ROOT%{_mandir}/man7
# I suspect that the core toolchain locale files will work with this reasonably well.
%{__rm} -r $RPM_BUILD_ROOT%{_localedir}

# Don't dupe the system libiberty.a
%if %{without bootstrap}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libiberty.a
%{__rm} $RPM_BUILD_ROOT%{archlib32dir}/libiberty.a
%{__rm} $RPM_BUILD_ROOT%{archlib64dir}/libiberty.a
%endif

%if %{with bootstrap}
# always create lib directories (place for newlib when bootstrapping)
install -d $RPM_BUILD_ROOT{%{archlib32dir},%{archlib64dir}}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README NEWS gcc/README.Portability
%attr(755,root,root) %{_bindir}/%{target}-cpp
%attr(755,root,root) %{_bindir}/%{target}-gcc
%attr(755,root,root) %{_bindir}/%{target}-gcc-%{version}
%attr(755,root,root) %{_bindir}/%{target}-gccbug
%attr(755,root,root) %{_bindir}/%{target}-gcov
%dir %{archlib32dir}
%dir %{archlib64dir}
%dir %{gccarchdir}
%dir %{gcclibdir}
%attr(755,root,root) %{gcclibdir}/cc1
%attr(755,root,root) %{gcclibdir}/collect2
%{gcclibdir}/crt*.o
%{gcclibdir}/libgcc.a
%{gcclibdir}/libgcov.a
%dir %{gcclibdir}/32
%{gcclibdir}/32/crt*.o
%{gcclibdir}/32/libgcc.a
%{gcclibdir}/32/libgcov.a
%dir %{gcclibdir}/include
%{gcclibdir}/include/ammintrin.h
%{gcclibdir}/include/avxintrin.h
%{gcclibdir}/include/bmmintrin.h
%{gcclibdir}/include/cpuid.h
%{gcclibdir}/include/cross-stdarg.h
%{gcclibdir}/include/emmintrin.h
%{gcclibdir}/include/float.h
%{gcclibdir}/include/immintrin.h
%{gcclibdir}/include/iso646.h
%{gcclibdir}/include/limits.h
%{gcclibdir}/include/mm3dnow.h
%{gcclibdir}/include/mm_malloc.h
%{gcclibdir}/include/mmintrin-common.h
%{gcclibdir}/include/mmintrin.h
%{gcclibdir}/include/nmmintrin.h
%{gcclibdir}/include/pmmintrin.h
%{gcclibdir}/include/smmintrin.h
%{gcclibdir}/include/stdarg.h
%{gcclibdir}/include/stdbool.h
%{gcclibdir}/include/stddef.h
%{gcclibdir}/include/stdfix.h
%{gcclibdir}/include/syslimits.h
%{gcclibdir}/include/tmmintrin.h
%{gcclibdir}/include/unwind.h
%{gcclibdir}/include/varargs.h
%{gcclibdir}/include/wmmintrin.h
%{gcclibdir}/include/x86intrin.h
%{gcclibdir}/include/xmmintrin.h
%{_mandir}/man1/%{target}-cpp.1*
%{_mandir}/man1/%{target}-gcc.1*
%{_mandir}/man1/%{target}-gcov.1*

%if %{without bootstrap}
%files c++
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-c++
%attr(755,root,root) %{_bindir}/%{target}-g++
%attr(755,root,root) %{gcclibdir}/cc1plus
%{archincludedir}/c++
%{archlib32dir}/libstdc++.a
%{archlib32dir}/libstdc++.la
%{archlib32dir}/libsupc++.a
%{archlib32dir}/libsupc++.la
%{archlib64dir}/libstdc++.a
%{archlib64dir}/libstdc++.la
%{archlib64dir}/libsupc++.a
%{archlib64dir}/libsupc++.la
%{_mandir}/man1/%{target}-g++.1*

%files objc
%defattr(644,root,root,755)
%attr(755,root,root) %{gcclibdir}/cc1obj
%{gcclibdir}/include/objc
%{archlib32dir}/libobjc.a
%{archlib32dir}/libobjc.la
%{archlib64dir}/libobjc.a
%{archlib64dir}/libobjc.la
%endif
