# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel

%global _scl_prefix %{ns_dir}
%global scl_name_base    %{ns_name}-php
%global scl_macro_base   %{ns_name}_php
%global scl_name_version 83
%global scl              %{scl_name_base}%{scl_name_version}
%scl_package %scl

Summary:       Package that installs PHP 8.3
Name:          %scl_name
Version:       8.3.23
Vendor:        cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define        release_prefix 1
Release:       %{release_prefix}%{?dist}.cpanel
Group:         Development/Languages
License:       GPLv2+

Source0:       macros-build
Source1:       README.md
Source2:       LICENSE
Source3:       whm_feature_addon

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: scl-utils-build
BuildRequires: help2man
# Temporary work-around
BuildRequires: iso-codes

Requires:      %{?scl_prefix}php-common
Requires:      %{?scl_prefix}php-cli

# Our code requires that pear be installed when the meta package is installed
Requires:      %{?scl_prefix}pear

%description
This is the main package for %scl Software Collection,
that install PHP 8.3 language.


%package runtime
Summary:   Package that handles %scl Software Collection.
Group:     Development/Languages
Requires:  scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary:   Package shipping basic build configuration
Group:     Development/Languages
Requires:  scl-utils-build

%description build
Package shipping essential configuration macros
to build %scl Software Collection.


%package scldevel
Summary:   Package shipping development files for %scl
Group:     Development/Languages

Provides:  ea-php-scldevel = %{version}
Conflicts: ea-php-scldevel > %{version}, ea-php-scldevel < %{version}

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.


%prep
%setup -c -T

cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF

# generate rpm macros file for depended collections
cat << EOF | tee scldev
%%scl_%{scl_macro_base}         %{scl}
%%scl_prefix_%{scl_macro_base}  %{scl_prefix}
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .


%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7


%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -D -m 644 enable %{buildroot}%{_scl_scripts}/enable
install -D -m 644 scldev %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel
install -D -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7
mkdir -p %{buildroot}/opt/cpanel/ea-php83/root/etc
mkdir -p %{buildroot}/opt/cpanel/ea-php83/root/usr/share/doc
mkdir -p %{buildroot}/opt/cpanel/ea-php83/root/usr/include
mkdir -p %{buildroot}/opt/cpanel/ea-php83/root/usr/share/man/man1
mkdir -p %{buildroot}/opt/cpanel/ea-php83/root/usr/bin
mkdir -p %{buildroot}/opt/cpanel/ea-php83/root/usr/var/cache
mkdir -p %{buildroot}/opt/cpanel/ea-php83/root/usr/var/tmp
mkdir -p %{buildroot}/opt/cpanel/ea-php83/root/usr/%{_lib}
mkdir -p %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures
install %{SOURCE3} %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures/%{name}

# Even if this package doesn't use it we need to do this because if another
# package does (e.g. pear licenses) it will be created and unowned by any RPM
%if 0%{?_licensedir:1}
mkdir %{buildroot}/%{_licensedir}
%endif

%scl_install

tmp_version=$(echo %{scl_name_version} | sed -re 's/([0-9])([0-9])/\1\.\2/')
sed -e 's/@SCL@/%{scl_macro_base}%{scl_name_version}/g' -e "s/@VERSION@/${tmp_version}/g" %{SOURCE0} \
  | tee -a %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Remove empty share/[man|locale]/ directories
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/man/ -type d -empty -delete
find %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale/ -type d -empty -delete
mkdir -p %{buildroot}/opt/cpanel/%{scl}/root/usr/share/locale

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files


%files runtime
%defattr(-,root,root)
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*
%dir /opt/cpanel/ea-php83/root/etc
%dir /opt/cpanel/ea-php83/root/usr
%dir /opt/cpanel/ea-php83/root/usr/share
%dir /opt/cpanel/ea-php83/root/usr/share/doc
%dir /opt/cpanel/ea-php83/root/usr/include
%dir /opt/cpanel/ea-php83/root/usr/share/man
%dir /opt/cpanel/ea-php83/root/usr/bin
%dir /opt/cpanel/ea-php83/root/usr/var
%dir /opt/cpanel/ea-php83/root/usr/var/cache
%dir /opt/cpanel/ea-php83/root/usr/var/tmp
%dir /opt/cpanel/ea-php83/root/usr/%{_lib}
%attr(644, root, root) /usr/local/cpanel/whostmgr/addonfeatures/%{name}
%if 0%{?_licensedir:1}
%dir %{_licensedir}
%endif

%files build
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl}-config


%files scldevel
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Thu Jul 03 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.3.23-1
- EA-13000: Update ea-php83 from v8.3.22 to v8.3.23

* Thu Jun 05 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.3.22-1
- EA-12917: Update ea-php83 from v8.3.21 to v8.3.22

* Thu May 08 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.3.21-1
- EA-12852: Update ea-php83 from v8.3.20 to v8.3.21

* Thu Apr 10 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.3.20-1
- EA-12807: Update ea-php83 from v8.3.19 to v8.3.20

* Thu Mar 13 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.3.19-1
- EA-12769: Update ea-php83 from v8.3.17 to v8.3.19

* Thu Feb 13 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.3.17-1
- EA-12708: Update ea-php83 from v8.3.16 to v8.3.17

* Thu Jan 16 2025 Cory McIntire <cory@cpanel.net> - 8.3.16-1
- EA-12650: Update ea-php83 from v8.3.15 to v8.3.16

* Thu Dec 19 2024 Cory McIntire <cory@cpanel.net> - 8.3.15-1
- EA-12618: Update ea-php83 from v8.3.14 to v8.3.15

* Thu Nov 21 2024 Cory McIntire <cory@cpanel.net> - 8.3.14-1
- EA-12578: Update ea-php83 from v8.3.13 to v8.3.14
- (Single byte overread with convert.quoted-printable-decode filter). (CVE-2024-11233)
- (Configuring a proxy in a stream context might allow for CRLF injection in URIs). (CVE-2024-11234)
- (Integer overflow in the dblib quoter causing OOB writes). (CVE-2024-11236)
- (Integer overflow in the firebird quoter causing OOB writes). (CVE-2024-11236)
- (Leak partial content of the heap through heap buffer over-read). (CVE-2024-8929)
- (OOB access in ldap_escape). (CVE-2024-8932)

* Thu Oct 24 2024 Cory McIntire <cory@cpanel.net> - 8.3.13-1
- EA-12497: Update ea-php83 from v8.3.12 to v8.3.13

* Thu Sep 26 2024 Cory McIntire <cory@cpanel.net> - 8.3.12-1
- EA-12410: Update ea-php83 from v8.3.11 to v8.3.12

* Tue Sep 24 2024 Julian Brown <julian.brown@cpanel.net> - 8.3.11-1
- ZC-12149: Update to v8.3.11

* Thu Aug 01 2024 Cory McIntire <cory@cpanel.net> - 8.3.10-1
- EA-12305: Update ea-php83 from v8.3.9 to v8.3.10

* Tue Jul 09 2024 Cory McIntire <cory@cpanel.net> - 8.3.9-1
- EA-12276: Update ea-php83 from v8.3.8 to v8.3.9

* Thu Jun 06 2024 Cory McIntire <cory@cpanel.net> - 8.3.8-1
- EA-12193: Update ea-php83 from v8.3.7 to v8.3.8

* Tue Jun 04 2024 Dan Muey <dan@cpanel.net> - 8.3.7-1
- EA-12145: Update ea-php83 from v8.3.6 to v8.3.7

* Thu Apr 11 2024 Cory McIntire <cory@cpanel.net> - 8.3.6-1
- EA-12086: Update ea-php83 from v8.3.4 to v8.3.6

* Thu Mar 14 2024 Cory McIntire <cory@cpanel.net> - 8.3.4-1
- EA-12018: Update ea-php83 from v8.3.3 to v8.3.4

* Thu Feb 15 2024 Cory McIntire <cory@cpanel.net> - 8.3.3-1
- EA-11978: Update ea-php83 from v8.3.2 to v8.3.3

* Thu Jan 18 2024 Cory McIntire <cory@cpanel.net> - 8.3.2-1
- EA-11920: Update ea-php83 from v8.3.1 to v8.3.2

* Thu Jan 04 2024 Cory McIntire <cory@cpanel.net> - 8.3.1-1
- EA-11894: Update ea-php83 from v8.3.0 to v8.3.1

* Thu Dec 14 2023 Julian Brown <julian.brown@cpanel.net> - 8.3.0-2
- ZC-11475: Build on CentOS 7

* Wed Sep 13 2023 Julian Brown <julian.brown@cpanel.net> - 8.3.0-1
- ZC-11182: Initial Build

