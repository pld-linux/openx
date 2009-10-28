# NOTES:
# - install doc: http://www.openx.org/docs/qsg-install
# TODO
# - System PKGS
#   - uses modified Smarty 2.6.18 ($oa_content arg to _compile_resource())
#   - uses modified ZendFramework 1.5.2 (disabled empty array casts in Zend/XmlRpc/Client.php)
# - FHS
#   - OpenX needs to be able to write to the files in the openx/var and openx/www/images folder to complete the installation successfully.
# - webapps
Summary:	OpenX allows you to traffic, target, monetize and track the advertising on all of your websites
Name:		openx
Version:	2.8.1
Release:	0.7
License:	GPL v2
Group:		Applications/WWW
Source0:	http://download.openx.org/%{name}-%{version}.zip
# Source0-md5:	9eed70d3ea24d06a11db03a546f0bf63
URL:		http://www.openx.org/ad-server
BuildRequires:	rpmbuild(macros) >= 1.461
Requires:	fonts-TTF-bitstream-vera
Requires:	php-common >= 4:5.1.4
Requires:	php-gd
Requires:	php-mysql
Requires:	php-zlib
Requires:	webapps
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}
%define		ttffontsdir	%{_fontsdir}/TTF

%description
OpenX is the world's leading independent ad server. It provides you
with the simple tools you need to make money from advertising, whether
from direct ad sales, OpenX Market, or third party ad networks (like
AdSense).

%package setup
Summary:	OpenX setup package
Summary(pl.UTF-8):	Pakiet do wstępnej konfiguracji OpenX
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}

%description setup
Install this package to configure initial OpenX installation. You
should uninstall this package when you're done, as it considered
insecure to keep the setup files in place.

%description setup -l pl.UTF-8
Ten pakiet należy zainstalować w celu wstępnej konfiguracji OpenX po
pierwszej instalacji. Potem należy go odinstalować, jako że
pozostawienie plików instalacyjnych mogłoby być niebezpieczne.

%prep
%setup -q

rm LICENSE.txt # GPL v2
rm var/UPGRADE # empty file
cat > docs/DB-ACL.txt <<'EOF'
# Database permissions needed:
SELECT
INSERT
UPDATE
DELETE
CREATE TABLE
DROP TABLE
CREATE INDEX
DROP INDEX
LOCK TABLES
EOF

cat > apache.conf <<'EOF'
Alias /%{name} %{_appdir}
<Directory %{_appdir}>
	Allow from all
</Directory>

<Directory %{_appdir}/etc>
	Deny from all
</Directory>

<Directory %{_appdir}/lib>
	Deny from all
</Directory>

<Directory %{_appdir}/var>
	Deny from all
</Directory>
EOF

cat > lighttpd.conf <<'EOF'
alias.url += (
    "/%{name}" => "%{_appdir}",
)
EOF

find -name .htaccess | xargs rm

# fix doc urls. pointed out on:
# http://forum.openx.org/index.php?s=4221111bd7f513019f5f12da048203ac&showtopic=503422007&mode=linearplus
sed -i -e '
#	s#".OX_PRODUCT_DOCSURL."/wizard/lock-config#http://www.openx.org/en/faq/installation/how-do-i-make-my-openx-installation-secure#
	s#".OX_PRODUCT_DOCSURL."/wizard/lock-config#http://www.openx.org/docs/2.8/adminguide/Securing+OpenX#
	s#".OX_PRODUCT_DOCSURL."/wizard/setup-cron#http://www.openx.org/en/docs/2.8/adminguide/Running+maintenance#
' lib/max/language/*/settings.lang.php

# fonts-TTF-bitstream-vera
sed -i -e "
	s#MAX_PATH.'/lib/fonts/Bitstream/#'%{ttffontsdir}/#
" lib/OA/Dashboard/Graph.php
rm -rf lib/fonts

# move all to docs subdir for easier packaging. except robots.txt
mv *.txt docs
mv docs/robots.txt .

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_appdir}}

cp -a apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -a apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -a lighttpd.conf $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf

cp -a *.php *.js *.txt $RPM_BUILD_ROOT%{_appdir}
cp -a etc lib maintenance plugins scripts var www $RPM_BUILD_ROOT%{_appdir}

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc docs/*
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
#%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*.php

%dir %{_appdir}

%{_appdir}/*.js
%{_appdir}/*.php
%{_appdir}/robots.txt
%{_appdir}/etc
%{_appdir}/lib
%{_appdir}/maintenance
%dir %{_appdir}/scripts
%{_appdir}/scripts/maintenance

%dir %attr(775,root,http) %{_appdir}/var
%dir %attr(775,root,http) %{_appdir}/var/cache
%dir %attr(775,root,http) %{_appdir}/var/plugins
%dir %attr(775,root,http) %{_appdir}/var/templates_compiled
%dir %attr(775,root,http) %{_appdir}/plugins

%dir %{_appdir}/www
%{_appdir}/www/*.php
%{_appdir}/www/api
%{_appdir}/www/delivery
%dir %attr(775,root,http) %{_appdir}/www/images
%{_appdir}/www/images/*

%{_appdir}/www/admin/precheck
%{_appdir}/www/robots.txt

%dir %{_appdir}/www/admin
%{_appdir}/www/admin/*.php
%{_appdir}/www/admin/*.js
%{_appdir}/www/admin/robots.txt
%{_appdir}/www/admin/*.html
%{_appdir}/www/admin/assets
%{_appdir}/www/admin/templates

%dir %attr(775,root,http) %{_appdir}/www/admin/plugins

%files setup
%defattr(644,root,root,755)
#%{_appdir}/www/admin
#%{_appdir}/etc/changes
