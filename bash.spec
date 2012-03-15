#%define beta_tag rc1
%define patchlevel .51
%define baseversion 3.2

Version: %{baseversion}%{patchlevel}
Name: bash
Summary: The GNU Bourne Again shell
Release: 1
Group: System/Shells
License: GPLv2+
Url: http://www.gnu.org/software/bash
Source0: ftp://ftp.gnu.org/gnu/bash/bash-3.2.48.tar.gz
Epoch: 1

# For now there isn't any doc
#Source2: ftp://ftp.gnu.org/gnu/bash/bash-doc-%{version}.tar.gz

Source1: dot-bashrc
Source2: dot-bash_profile
Source3: dot-bash_logout

# Official upstream patches
Patch049: ftp://ftp.gnu.org/pub/gnu/bash/bash-3.2-patches/bash32-049
Patch050: ftp://ftp.gnu.org/pub/gnu/bash/bash-3.2-patches/bash32-050
Patch051: ftp://ftp.gnu.org/pub/gnu/bash/bash-3.2-patches/bash32-051

# Other patches
Patch100: bash-2.03-paths.patch
Patch101: bash-2.02-security.patch
Patch102: bash-2.03-profile.patch
Patch103: bash-requires.patch
Patch107: bash-2.05a-interpreter.patch
Patch108: bash-2.05b-readline-oom.patch
Patch114: bash-2.05b-xcc.patch
Patch115: bash-2.05b-pgrp_sync.patch
Patch116: bash-2.05b-manso.patch
Patch117: bash-2.05b-debuginfo.patch
Patch118: bash-tty-tests.patch
Patch126: bash-setlocale.patch
Patch130: bash-infotags.patch
Patch131: bash-cond-rmatch.patch
Patch132: bash-ulimit-m.patch
Patch133: bash-3.2-rng.patch
Patch136: bash-3.2-344411.patch
Patch137: bash-3.2-190350.patch
Patch138: bash-3.2-comp_wordbreaks.patch
Patch139: bash-3.2-manpage.patch
Patch140: bash-3.2-man-page-suspend.patch
Patch141: bash-3.2-patch035.patch
Patch142: bash-3.2-execve_catch_signals.patch
Patch143: bash-3.2-ssh_source_bash.patch
Patch144: bash-3.2-command_not_found.patch
Patch145: bash-3.2-audit.patch
Patch146: bash-3.2-fc.patch

Requires(post): ncurses-libs
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: texinfo bison
BuildRequires: ncurses-devel
BuildRequires: autoconf, gettext

%description
The GNU Bourne Again shell (Bash) is a shell or command language
interpreter that is compatible with the Bourne shell (sh). Bash
incorporates useful features from the Korn shell (ksh) and the C shell
(csh). Most sh scripts can be run by bash without modification.

%package doc
Summary: Documentation files for %{name}
Group: Development/Languages
Requires: %{name} = %{version}-%{release}

%description doc
This package contains documentation files for %{name}.

%define pkgdocdir %{_datadir}/doc/%{name}-%{version}

%prep
#%setup -q -a 2
%setup -q -n %{name}-%{baseversion}.48

# Official upstream patches
%patch049 -p0 -b .049
%patch050 -p0 -b .050
%patch051 -p0 -b .051

# Other patches
%patch100 -p1 -b .paths
%patch101 -p1 -b .security
%patch102 -p1 -b .profile
%patch103 -p1 -b .requires
%patch107 -p1 -b .interpreter
%patch108 -p1 -b .readline-oom
%patch114 -p1 -b .xcc
%patch115 -p1 -b .pgrp_sync
%patch116 -p1 -b .manso
%patch117 -p1 -b .debuginfo
%patch118 -p1 -b .tty-tests
%patch126 -p1 -b .setlocale
%patch130 -p1 -b .infotags
%patch131 -p1 -b .cond-rmatch
%patch132 -p1 -b .ulimit-m
%patch133 -p1 -b .rng.patch
%patch136 -p1 -b .344411
%patch137 -p1 -b .190350
%patch138 -p1 -b .comp_wordbreaks
%patch139 -p1 -b .manpage
%patch140 -p1 -b .man-page-suspend
%patch142 -p1 -b .execve_catch_signals
%patch143 -p1 -b .ssh_source_bash
%patch144 -p1 -b .command_not_found
%patch145 -p1 -b .audit
%patch146 -p1 -b .fc

echo %{version} > _distribution
echo %{release} > _patchlevel

%build
autoconf
%configure --with-bash-malloc=no --with-afs

# Recycles pids is neccessary. When bash's last fork's pid was X
# and new fork's pid is also X, bash has to wait for this same pid.
# Without Recycles pids bash will not wait.
make "CPPFLAGS=-D_GNU_SOURCE -DRECYCLES_PIDS `getconf LFS_CFLAGS`"
%check
make check

%install
rm -rf $RPM_BUILD_ROOT

if [ -e autoconf ]; then
  # Yuck. We're using autoconf 2.1x.
  export PATH=.:$PATH
fi

# Fix bug #83776
perl -pi -e 's,bashref\.info,bash.info,' doc/bashref.info

make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT/etc

# make manpages for bash builtins as per suggestion in DOC/README
pushd doc
sed -e '
/^\.SH NAME/, /\\- bash built-in commands, see \\fBbash\\fR(1)$/{
/^\.SH NAME/d
s/^bash, //
s/\\- bash built-in commands, see \\fBbash\\fR(1)$//
s/,//g
b
}
d
' builtins.1 > man.pages
for i in echo pwd test kill; do
  perl -pi -e "s,$i,,g" man.pages
  perl -pi -e "s,  , ,g" man.pages
done

install -c -m 644 builtins.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/builtins.1

for i in `cat man.pages` ; do
  echo .so man1/builtins.1 > ${RPM_BUILD_ROOT}%{_mandir}/man1/$i.1
  chmod 0644 ${RPM_BUILD_ROOT}%{_mandir}/man1/$i.1
done
popd

# Link bash man page to sh so that man sh works.
ln -s bash.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/sh.1

# Not for printf, true and false (conflict with coreutils)
rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/printf.1
rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/true.1
rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/false.1

pushd $RPM_BUILD_ROOT
mkdir ./bin
mv ./usr/bin/bash ./bin
ln -sf bash ./bin/sh
rm -f .%{_infodir}/dir
popd
mkdir -p $RPM_BUILD_ROOT/etc/skel
install -c -m644 %SOURCE1 $RPM_BUILD_ROOT/etc/skel/.bashrc
install -c -m644 %SOURCE2 $RPM_BUILD_ROOT/etc/skel/.bash_profile
install -c -m644 %SOURCE3 $RPM_BUILD_ROOT/etc/skel/.bash_logout
LONG_BIT=$(getconf LONG_BIT)
mv $RPM_BUILD_ROOT%{_bindir}/bashbug \
   $RPM_BUILD_ROOT%{_bindir}/bashbug-"${LONG_BIT}"

# Fix missing sh-bangs in example scripts (bug #225609).
for script in \
  examples/scripts/krand.bash \
  examples/scripts/bcsh.sh \
  examples/scripts/precedence \
  examples/scripts/shprompt
do
  cp "$script" "$script"-orig
  echo '#!/bin/bash' > "$script"
  cat "$script"-orig >> "$script"
  rm -f "$script"-orig
done

chmod a-x doc/*.sh
%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

# ***** bash doesn't use install-info. It's always listed in %{_infodir}/dir
# to prevent prereq loops

# post is in lua so that we can run it without any external deps.  Helps
# for bootstrapping a new install.
# Jesse Keating 2009-01-29 (code from Ignacio Vazquez-Abrams)
%post -p <lua>
bashfound = false;
shfound = false;
 
f = io.open("/etc/shells", "r");
if f == nil
then
  f = io.open("/etc/shells", "w");
else
  repeat
    t = f:read();
    if t == "/bin/bash"
    then
      bashfound = true;
    end
    if t == "/bin/sh"
    then
      shfound = true;
    end
  until t == nil;
end
f:close()
 
f = io.open("/etc/shells", "a");
if not bashfound
then
  f:write("/bin/bash\n")
end
if not shfound
then
  f:write("/bin/sh\n")
end
f:close()

%postun
if [ "$1" = 0 ]; then
    /bin/grep -v '^/bin/bash$' < /etc/shells | \
      /bin/grep -v '^/bin/sh$' > /etc/shells.new
    /bin/mv /etc/shells.new /etc/shells
fi

%docs_package

%lang_package

%files 
%defattr(-,root,root,-)
%config(noreplace) /etc/skel/.b*
/bin/sh
/bin/bash
%attr(0755,root,root) %{_bindir}/bashbug-*

