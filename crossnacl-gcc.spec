#
# Conditional build:
%bcond_with	bootstrap		# build without NaCL newlib package dependency (without c++ package)

%define		gitver	455063d
Summary:	Various compilers (C, C++) for NaCl
Name:		crossnacl-gcc
Version:	4.4.3
Release:	6.git%{gitver}
License:	GPL v3+ and GPL v3+ with exceptions and GPL v2+ with exceptions
Group:		Development/Languages
Source0:	nacl-gcc-%{version}-git%{gitver}.tar.xz
# Source0-md5:	dd49a8726695a06c7fe9fc531dc6c637
Source1:	get-source.sh
URL:		http://sourceware.org/gcc/
BuildRequires:	cloog-ppl-devel
BuildRequires:	crossnacl-binutils
BuildRequires:	elfutils-devel
BuildRequires:	gmp-c++-devel
BuildRequires:	gmp-devel
BuildRequires:	mpfr-devel
BuildRequires:	ppl-pwl-devel
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildConflicts:	cloog-isl-devel
%if %{without bootstrap}
BuildRequires:	crossnacl-newlib
%endif
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		target		x86_64-nacl
%define		arch		%{_prefix}/%{target}
%define		gcc_ver		%{version}
%define		gcclib		%{_libdir}/gcc/%{target}/%{gcc_ver}
%define		gccnlib		%{_prefix}/lib/gcc/%{target}/%{gcc_ver}

%define		filterout_cpp	-D_FORTIFY_SOURCE=[0-9]+
%define		filterout_c		-Werror=format-security

%description
The gcc package contains the GNU Compiler Collection version 4.4.3.
You'll need this package in order to compile C code.

This provides support for NaCl targets.

%package c++
Summary:	C++ support for crossnacl-gcc
Summary(pl.UTF-8):	Obsługa C++ dla crossnacl-gcc
Group:		Development/Languages
Requires:	%{name} = %{version}-%{release}

%description c++
This package adds C++ support to the GNU Compiler Collection for NaCl
targets.

%description c++ -l pl.UTF-8
Ten pakiet dodaje obsługę C++ do kompilatora gcc dla NaCL.

%package objc
Summary:	NaCL binary utility development utilities - objc
Summary(pl.UTF-8):	Zestaw narzędzi NaCL - objc
Group:		Development/Languages
Requires:	%{name} = %{version}-%{release}

%description objc
This package contains cross targeted objc compiler.

%description objc -l pl.UTF-8
Ten pakiet zawiera kompilator objc generujący kod pod Win32.

%prep
%setup -q -n nacl-gcc-%{version}-git%{?gitver}

%build
rm -rf obj-%{target}
install -d obj-%{target}
cd obj-%{target}

OPT_FLAGS="%{rpmcflags}"
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
	--prefix=%{_prefix} \
	--mandir=%{_mandir} \
	--infodir=%{_infodir} \
	--libexecdir=%{_libdir} \
	--enable-checking=release \
	--with-system-zlib \
	--enable-__cxa_atexit \
	--disable-libunwind-exceptions \
	--enable-gnu-unique-object \
	--disable-decimal-float \
	--disable-libgomp \
	--disable-libmudflap \
	--disable-libssp \
	--disable-libstdcxx-pch \
	--disable-shared \
	--with-ppl --with-cloog \
	CC="%{__cc}" \
	CFLAGS="$OPT_FLAGS $GCC_DEFINES" \
	CXXFLAGS="$(echo $OPT_FLAGS | sed 's/ -Wall / /g')" \
	XCFLAGS="$OPT_FLAGS" \
%if %{with bootstrap}
	--disable-threads \
	--enable-languages="c" \
	--without-headers \
	CFLAGS_FOR_TARGET="-O2 -g" \
	CXXFLAGS_FOR_TARGET="-O2 -g" \
%else
	CFLAGS_FOR_TARGET="-O2 -g -mtls-use-call -I/usr/x86_64-nacl/include/" \
	CXXFLAGS_FOR_TARGET="-O2 -g -mtls-use-call -I/usr/x86_64-nacl/include/" \
	--enable-threads=nacl \
	--enable-languages="c,c++,objc" \
	--enable-tls \
	--with-newlib \
%endif
	--target=%{target} \
	--with-host-libstdcxx="-lpwl -lstdc++ -lm" \
	--disable-ppl-version-check \
	--disable-libgcj

%{__make} \
	BOOT_CFLAGS="$OPT_FLAGS" \
%if %{with bootstrap}
	all-gcc all-target-libgcc
%else
	all
%endif

%install
rm -rf $RPM_BUILD_ROOT
cd obj-%{target}
%{__make} \
%if %{with bootstrap}
	install-gcc install-target-libgcc \
%else
	install \
%endif
	DESTDIR=$RPM_BUILD_ROOT

# move fixed includes to proper place
mv $RPM_BUILD_ROOT%{gccnlib}/include-fixed/*.h $RPM_BUILD_ROOT%{gccnlib}/include

%{__rm} -r $RPM_BUILD_ROOT%{gccnlib}/include-fixed
%{__rm} -r $RPM_BUILD_ROOT%{gccnlib}/install-tools

# Delete supplemental files that would conflict with the core toolchain
%{__rm} -r $RPM_BUILD_ROOT%{_infodir}
%{__rm} -r $RPM_BUILD_ROOT%{_mandir}/man7
# I suspect that the core toolchain locale files will work with this reasonably well.
%{__rm} -r $RPM_BUILD_ROOT%{_localedir}

# Don't dupe the system libiberty.a
%if %{without bootstrap}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libiberty.a
%{__rm} $RPM_BUILD_ROOT%{_prefix}/%{target}/lib*/libiberty.a
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc gcc/README*
%attr(755,root,root) %{_bindir}/%{target}-cpp
%attr(755,root,root) %{_bindir}/%{target}-gcc
%attr(755,root,root) %{_bindir}/%{target}-gcc-%{gcc_ver}
%attr(755,root,root) %{_bindir}/%{target}-gccbug
%attr(755,root,root) %{_bindir}/%{target}-gcov

%if "%{_lib}" != "lib"
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{target}
%dir %{gccnlib}
%endif

%{gccnlib}/*.[ao]
%dir %{gccnlib}/include
%{gccnlib}/include/*.h

%dir %{gccnlib}/32
%{gccnlib}/32/*.[oa]

%dir %{_libexecdir}
%dir %{_libexecdir}/gcc
%dir %{_libexecdir}/gcc/%{target}
%dir %{gcclib}
%attr(755,root,root) %{gcclib}/cc1
%attr(755,root,root) %{gcclib}/collect2

%if "%{_lib}" != "lib"
# not present on ix86, not needed?
%dir %{gcclib}/install-tools
%attr(755,root,root) %{gcclib}/install-tools/*
%endif

%{_mandir}/man1/%{target}-cpp.*
%{_mandir}/man1/%{target}-gcc.*
%{_mandir}/man1/%{target}-gcov.*

%if %{without bootstrap}
%files c++
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{target}-c++
%attr(755,root,root) %{_bindir}/%{target}-g++
%attr(755,root,root) %{gcclib}/cc1plus
%{_prefix}/%{target}/include/c++
%dir %{_prefix}/%{target}/lib32
%dir %{_prefix}/%{target}/lib64
%{_prefix}/%{target}/lib*/libstdc++.*a
%{_prefix}/%{target}/lib*/libsupc++.*a
%{_mandir}/man1/%{target}-g++.*

%files objc
%defattr(644,root,root,755)
%attr(755,root,root) %{gcclib}/cc1obj
%{_prefix}/%{target}/lib*/libobjc.*a
%{gccnlib}/include/objc
%endif
