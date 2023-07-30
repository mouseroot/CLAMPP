import requests, os, sys
import shutil


msvc_redist = "https://aka.ms/vs/17/release/VC_redist.x64.exe"
apache2 = "https://archive.apache.org/dist/httpd/binaries/win32/apache_2.2.9-win32-x86-openssl-0.9.8h-r2.msi"
apache2_zip = "https://www.apachelounge.com/download/VS17/binaries/httpd-2.4.57-win64-VS17.zip"
php8 = "https://windows.php.net/downloads/releases/php-8.2.8-Win32-vs16-x64.zip"
maria_db = "https://mirrors.gigenet.com/mariadb/mariadb-11.1.1/winx64-packages/mariadb-11.1.1-winx64.zip"
phpmyadmin = "https://files.phpmyadmin.net/phpMyAdmin/5.2.1/phpMyAdmin-5.2.1-all-languages.zip"
composer = "https://getcomposer.org/Composer-Setup.exe"

stage_dir = "_staging"
install_dir = "C:\\CLAMPP\\"

htdocs = f"{install_dir}Apache24\\htdocs\\"
apache_bin = f"{install_dir}Apache24\\bin\\"
php_bin = f"{install_dir}php8.2\\"

#Ripped from https://kodify.net/python/remove-folder-recursively/#remove-folders-recursively-with-osrmdir
def remove_directory_tree(start_directory: str):
    try:
        """Recursively and permanently removes the specified directory, all of its
        subdirectories, and every file contained in any of those folders."""
        for name in os.listdir(start_directory):
            path = os.path.join(start_directory, name)
            if os.path.isfile(path):
                os.remove(path)
            else:
                remove_directory_tree(path)
        os.rmdir(start_directory)
    except FileNotFoundError:
        return

def download(url, filename):
    r = requests.get(url, allow_redirects=True,headers={"User-Agent":"Mozilla 4.0"})
    open(filename, 'wb').write(r.content)

def banner():
    print("\t[#] CLAMPP Installer v0.5")
    print("\t[#] Composer | Laravel | Apache2 | MariaDB | PHP | PHPMyAdmin")
    print()
    print("\t[i] The Future is in the Past, and The Future is the CLAMPP Stack!")
    print("\t[i] Get Up and running with the full setup or just install what you need.")
    print()

def menu():
    print("\t[1] Install CLAMPP")
    print("\t[2] Run Apache2 ")

def write_launcher_bat():
    bat_file = f"""@echo off
echo CLAMPP Shell v0.1
cmd /k "set PATH=%PATH%;{install_dir}Apache24/bin;{install_dir}php8.2/;{install_dir}mariadb-11.1.1-winx64/bin/";    
"""
    with open(f"{install_dir}Shell.bat","w") as batch_f:
        batch_f.write(bat_file)
    print("\t[!] Created Shell.bat")

def remove_stage_dir():
    print("\t[X] Removing existing staging files...")
    remove_directory_tree(stage_dir)

def remove_install_dir():
    print("\t[X] Removing install directory...")
    remove_directory_tree(install_dir)

def create_stage_dir():
    print("\t[!] Creating Staging Dir")
    os.mkdir(stage_dir)

def create_install_dir():
    print("\t[i] Creating Install Dir")
    os.mkdir(f"{install_dir}")

def download_redist():
    print("\t[!] Downloading VC++ Redist....")
    download(msvc_redist,f"{stage_dir}\\redist.exe")

def download_apache2():
    print("\t[!] Downloading Apache2...")
    download(apache2_zip,f"{stage_dir}\\apache2.zip")

def download_php8():
    print("\t[!] Download PHP8.2...")
    download(php8,f"{stage_dir}\\php8.zip")

def download_phpmyadmin():
    print("\t[!] Downloading phpmyadmin...")
    download(phpmyadmin,f"{stage_dir}\\phpmyadmin.zip")

def download_maria():
    print("\t[!] Downloading MariaDB...")
    download(maria_db,f"{stage_dir}\\maria.zip")

def install_redist():
    print("\t[!] Installing Redist...")
    os.system(f"{stage_dir}\\redist.exe /Q")

def install_apache2():
    print("\t[!] Installing Apache2...")
    #os.system(f"msiexec /i {stage_dir}\\apache2.msi INSTALLDIR={install_dir}\\bin\\apache2 /passive /qn")
    os.system(f"7z x {stage_dir}\\apache2.zip -o{install_dir} >nul 2>&1")

def install_php8():
    print("\t[!] Installing PHP 8.2...")
    os.system(f"7z x {stage_dir}\\php8.zip -o{install_dir}php8.2\\ >nul 2>&1")

def install_maria():
    print("\t[!] Installing MariaDB...")
    os.system(f"7z x {stage_dir}\\maria.zip -o{install_dir} >nul 2>&1")

def install_phpmyadmin():
    print("\t[!] Installing phpmyadmin..")
    os.system(f"7z x {stage_dir}\\phpmyadmin.zip -o{htdocs} >nul 2>&1")
    os.rename(f"{htdocs}phpMyAdmin-5.2.1-all-languages" ,f"{htdocs}phpMyAdmin")

def config_php():
    print("\t[!] Configuring PHP 8.2")
    shutil.copy(f"{php_bin}php.ini-development",f"{php_bin}php.ini")
    phpini_data = open(f"{install_dir}\\php8.2\\php.ini","r").read()
    phpini_data = phpini_data.replace(';extension_dir = "ext"','extension_dir = "ext"')
    phpini_data = phpini_data.replace(';extension=mysqli','extension=mysqli')

    with open(f"{install_dir}php8.2\\php.ini","w") as out_phpini:
        out_phpini.write(phpini_data)
        out_phpini.write("extension=curl\n") # Add Laravel Exts
        out_phpini.write("extension=fileinfo\n")
        out_phpini.write("extension=mbstring\n")
        out_phpini.write("extension=pdo_mysql\n")
        out_phpini.write("extension=sockets\n")
        out_phpini.write("extension=zip\n")
        out_phpini.write("extension=openssl\n")

def config_apache2():
    print("\t[!] Configuring Apache2")
    php_mod_settings = f"""
# PHP 8.2 Config (PAM)
PHPIniDir {install_dir}/php8.2
LoadModule php_module {install_dir}/php8.2/php8apache2_4.dll
AddType application/x-httpd-php .php
"""

    apache2_conf = open(f"{install_dir}\\Apache24\\conf\\httpd.conf","r")
    conf_block = apache2_conf.read()
    apache2_conf.close()
    conf_block = conf_block.replace("c:/Apache24",f"{install_dir}/Apache24/")
    conf_block = conf_block.replace("DirectoryIndex index.html","DirectoryIndex index.php index.html")
    conf_block = conf_block.replace('ServerRoot "${SRVROOT}"','ServerRoot "${SRVROOT}"\nServerName "PAM"')

    apache2_conf = open(f"{install_dir}\\Apache24\\conf\\httpd.conf","w")
    conf_block += php_mod_settings
    apache2_conf.write(conf_block)
    apache2_conf.close()

    test_php = """
    <a href="localhost:80/phpMyAdmin/">phpMyAdmin</a><br />
    <?php
    phpinfo();
    ?>
    """
    shutil.move(f"{install_dir}\\Apache24\\htdocs\\index.html",f"{install_dir}\\Apache24\\htdocs\\index.php")
    with open(f"{install_dir}\\Apache24\\htdocs\\index.php","w") as indexphp:
        indexphp.write(test_php)
    print("\t[!] Added index.php")

def test_config():
    print("\t[?] Testing Configuration...")
    os.system(f"{install_dir}\\Apache24\\bin\\httpd.exe -t")


#print("\t[!] Installing Composer")

#print("\t[!] Installing Laravel")
def laravel_project(name):
    print(f"Building {name} Laravel Project...")
    os.system(f"cd {htdocs} &&  composer create-project laravel/laravel {name}")
    os.system(f"cd {htdocs}\\{name} && {php_bin}\\php.exe artisan serv")


if __name__ == "__main__":
    banner()
    menu()
    try:
        sel = int(input("\t?"))
        if sel == 1:
            #remove_stage_dir()
            remove_install_dir()

            #create_stage_dir()
            create_install_dir()

            #download_redist()
            #download_apache2()
            #download_php8()
            #download_phpmyadmin()
            #download_maria()

            #install_redist()
            install_apache2()
            install_maria()
            install_php8()
            install_phpmyadmin()

            config_apache2()
            config_php()
            test_config()
            #laravel_project(input("Enter a Project Name: "))
            write_launcher_bat()
            os.system(f"{install_dir}Shell.bat")
            print("\t[!] Ready")
        elif sel == 2:
            print("\t[i] Starting Apache2...")
            print("\t[i] Ctrl+C to Stop Server")
            import subprocess, time
            httpd = subprocess.Popen([f"{apache_bin}httpd.exe"])
            while httpd.poll() is None:
                time.sleep(1)
            print("\t[x] Apache2 Stopped")
            
    except KeyboardInterrupt:
        pass

