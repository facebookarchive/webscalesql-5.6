2.4 Installing MySQL on OS X

   For a list of supported OS X versions that the MySQL server
   supports, see
   http://www.mysql.com/support/supportedplatforms/database.html
   .

   MySQL for OS X is available in a number of different forms:

     * Native Package Installer format, which uses the native OS
       X installer (DMG) to walk you through the installation of
       MySQL. For more information, see Section 2.4.2,
       "Installing MySQL on OS X Using Native Packages." You can
       use the package installer with OS X. The user you use to
       perform the installation must have administrator
       privileges.

     * Tar package format, which uses a file packaged using the
       Unix tar and gzip commands. To use this method, you will
       need to open a Terminal window. You do not need
       administrator privileges using this method, as you can
       install the MySQL server anywhere using this method. For
       more information on using this method, you can use the
       generic instructions for using a tarball, Section 2.2,
       "Installing MySQL on Unix/Linux Using Generic Binaries."
       In addition to the core installation, the Package
       Installer also includes Section 2.4.4, "Installing the
       MySQL Startup Item" and Section 2.4.5, "Installing and
       Using the MySQL Preference Pane," both of which simplify
       the management of your installation.

   For additional information on using MySQL on OS X, see
   Section 2.4.1, "General Notes on Installing MySQL on OS X."

2.4.1 General Notes on Installing MySQL on OS X

   You should keep the following issues and notes in mind:

     * OS X 10.4 deprecated startup items in favor of launchd
       daemons, and as of OS X 10.10 (Yosemite), startup items
       do not function. For these reasons, using launchd daemons
       is preferred over startup items.

     * You may need (or want) to create a specific mysql user to
       own the MySQL directory and data. You can do this through
       the Directory Utility, and the mysql user should already
       exist. For use in single user mode, an entry for _mysql
       (note the underscore prefix) should already exist within
       the system /etc/passwd file.

     * If you get an "insecure startup item disabled" error when
       MySQL launches, use the following procedure. Adjust the
       pathnames appropriately for your system.

         1. Modify the mysql.script using this command (enter it
            on a single line):
shell> sudo /Applications/TextEdit.app/Contents/MacOS/TextEdit
  /usr/local/mysql/support-files/mysql.server


         2. Locate the option file that defines the basedir
            value and modify it to contain these lines:
basedir=/usr/local/mysql
datadir=/usr/local/mysql/data

            In the /Library/StartupItems/MySQLCOM/ directory,
            make the following group ID changes from staff to
            wheel:
shell> sudo chgrp wheel MySQLCOM StartupParameters.plist


         3. Start the server from System Preferences or
            Terminal.app.

     * Because the MySQL package installer installs the MySQL
       contents into a version and platform specific directory,
       you can use this to upgrade and migrate your database
       between versions. You will need to either copy the data
       directory from the old version to the new version, or
       alternatively specify an alternative datadir value to set
       location of the data directory. By default, the MySQL
       directories are installed under /usr/local/.

     * You might want to add aliases to your shell's resource
       file to make it easier to access commonly used programs
       such as mysql and mysqladmin from the command line. The
       syntax for bash is:
alias mysql=/usr/local/mysql/bin/mysql
alias mysqladmin=/usr/local/mysql/bin/mysqladmin

       For tcsh, use:
alias mysql /usr/local/mysql/bin/mysql
alias mysqladmin /usr/local/mysql/bin/mysqladmin

       Even better, add /usr/local/mysql/bin to your PATH
       environment variable. You can do this by modifying the
       appropriate startup file for your shell. For more
       information, see Section 4.2.1, "Invoking MySQL
       Programs."

     * After you have copied over the MySQL database files from
       the previous installation and have successfully started
       the new server, you should consider removing the old
       installation files to save disk space. Additionally, you
       should also remove older versions of the Package Receipt
       directories located in
       /Library/Receipts/mysql-VERSION.pkg.

     * Prior to OS X 10.7, MySQL server was bundled with OS X
       Server.

2.4.2 Installing MySQL on OS X Using Native Packages

   The package is located inside a disk image (.dmg) file that
   you first need to mount by double-clicking its icon in the
   Finder. It should then mount the image and display its
   contents.
   Note

   Before proceeding with the installation, be sure to stop all
   running MySQL server instances by using either the MySQL
   Manager Application (on OS X Server) or mysqladmin shutdown
   on the command line.

   When installing from the package version, you can also
   install the MySQL Preference Pane, which will enable you to
   control the startup and execution of your MySQL server from
   System Preferences. For more information, see Section 2.4.5,
   "Installing and Using the MySQL Preference Pane."

   When installing using the package installer, the files are
   installed into a directory within /usr/local matching the
   name of the installation version and platform. For example,
   the installer file mysql-5.6-osx10.8-x86_64.dmg installs
   MySQL into /usr/local/mysql-5.6-osx10.8-x86_64/ . The
   following table shows the layout of the installation
   directory.

   Table 2.5 MySQL Installation Layout on OS X
   Directory Contents of Directory
   bin, scripts mysqld server, client and utility programs
   data Log files, databases
   docs Helper documents, like the Release Notes and build
   information
   include Include (header) files
   lib Libraries
   man Unix manual pages
   mysql-test MySQL test suite
   share Miscellaneous support files, including error messages,
   sample configuration files, SQL for database installation
   sql-bench Benchmarks
   support-files Scripts and sample configuration files
   /tmp/mysql.sock Location of the MySQL Unix socket

   During the package installer process, a symbolic link from
   /usr/local/mysql to the version/platform specific directory
   created during installation will be created automatically.

    1. Download and open the MySQL package installer, which is
       provided on a disk image (.dmg) that includes the main
       MySQL installation package file. Double-click the disk
       image to open it.
       Figure 2.40 MySQL Package Installer: DMG Contents
       MySQL Package Installer: DMG Contents

    2. Double-click the MySQL installer package. It will be
       named according to the version of MySQL you have
       downloaded. For example, if you have downloaded MySQL
       server 5.6.25, double-click
       mysql-5.6.25-osx-10.8-x86_64.pkg.

    3. You will be presented with the opening installer dialog.
       Click Continue to begin installation.
       Figure 2.41 MySQL Package Installer: Introduction
       MySQL Package Installer: Introduction

    4. If you have downloaded the community version of MySQL,
       you will be shown a copy of the relevant GNU General
       Public License. Click Continue and then Agree to
       continue.

    5. From the Installation Type page you can either click
       Install to execute the installation wizard using all
       defaults, click Customize to alter which components to
       install (MySQL server, Startup Item, Preference Pane --
       all enabled by default), or click Change Installation
       Location to change the type of installation for either
       all users, only the user executing the Installer, or
       define a custom location.
       Figure 2.42 MySQL Package Installer: Installation Type
       MySQL Package Installer: Installation Type
       Figure 2.43 MySQL Package Installer: Destination Select
       (Change Installation Location)
       MySQL Package Installer: Destination Select (Change
       Installation Location)
       Figure 2.44 MySQL Package Installer: Customize
       MySQL Package Installer: Customize

    6. Click Install to begin the installation process.

    7. Once the installation has been completed successfully,
       you will be shown an Install Succeeded message with a
       short summary. Now, Close the wizard and begin using the
       MySQL server.
       Figure 2.45 MySQL Package Installer: Summary
       MySQL Package Installer: Summary

   For convenience, you may also want to install a launch daemon
   and preference pane. See Section 2.4.3, "Installing a MySQL
   Launch Daemon," and Section 2.4.5, "Installing and Using the
   MySQL Preference Pane."

2.4.3 Installing a MySQL Launch Daemon

   OS X uses launch daemons to automatically start, stop, and
   manage processes and applications such as MySQL. Using launch
   daemons is recommended over startup items on OS X.
   Note

   OS X 10.4 deprecated startup items in favor of launchd
   daemons, and as of OS X 10.10 (Yosemite), startup items do
   not function. For these reasons, using launchd daemons is
   preferred over startup items.

   Here is an example launchd file that starts MySQL:

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>KeepAlive</key>
    <true/>
    <key>Label</key>
    <string>com.mysql.mysqld</string>
    <key>ProgramArguments</key>
    <array>
    <string>/usr/local/mysql/bin/mysqld_safe</string>
    <string>--user=mysql</string>
    </array>
  </dict>
</plist>


   Adjust the ProgramArguments array according to your system,
   as for example your path to mysqld_safe might be different.
   After making the proper adjustments, do the following:

     * Save the XML as a file named
       /Library/LaunchDaemons/com.mysql.mysql.plist

     * Adjust the file permissions using the Apple recommended
       owner "root", owning group "wheel", and file permissions
       "644"
shell> sudo chown root:wheel /Library/LaunchDaemons/com.mysql.mysql.pl
ist
shell> sudo chmod 644 /Library/LaunchDaemons/com.mysql.mysql.plist


     * Enable this new MySQL service
shell> sudo launchctl load -w /Library/LaunchDaemons/com.mysql.mysql.p
list

   The MySQL daemon is now running, and automatically starts
   when your system is rebooted.

2.4.4 Installing the MySQL Startup Item

   The MySQL Installation Package includes a startup item that
   can be used to automatically start and stop MySQL.
   Important

   Startup items are deprecated in favor of launchd daemons. For
   additional information, see Section 2.4.3, "Installing a
   MySQL Launch Daemon."

   To install the MySQL Startup Item:

    1. Download and open the MySQL package installer, which is
       provided on a disk image (.dmg) that includes the main
       MySQL installation package.
       Note
       Previously, the OS X packages included separate
       MySQLStartupItem.pkg and MySQL.prefPane files. They have
       since been merged into the main package file.
       Figure 2.46 MySQL Package Installer: DMG Contents
       MySQL Package Installer: DMG Contents

    2. Go through the process of installing the MySQL server as
       described in the documentation at Section 2.4.2,
       "Installing MySQL on OS X Using Native Packages."

    3. Click Customize at the Installation Type step. The
       "Startup Item" option is listed there and enabled by
       default.
       Figure 2.47 MySQL Installer on OS X: Customize
       MySQL Installer on OS X: Customize

    4. Complete the MySQL server installation process.

   The Startup Item for MySQL is installed into
   /Library/StartupItems/MySQLCOM. The Startup Item installation
   adds a variable MYSQLCOM=-YES- to the system configuration
   file /etc/hostconfig. If you want to disable the automatic
   startup of MySQL, change this variable to MYSQLCOM=-NO-.
   Note

   Deselecting Automatically Start MySQL Server on Startup from
   the MySQL Preference Pane sets the MYSQLCOM variable to -NO-.

   After the installation, you can start and stop the MySQL
   server from the MySQL Preference Pane (preferred), or by
   running the following commands in a terminal window. You must
   have administrator privileges to perform these tasks, and you
   may be prompted for your password.

   If you have installed the Startup Item, use this command to
   start the server:
shell> sudo /Library/StartupItems/MySQLCOM/MySQLCOM start

   If you have installed the Startup Item, use this command to
   stop the server:
shell> sudo /Library/StartupItems/MySQLCOM/MySQLCOM stop

2.4.5 Installing and Using the MySQL Preference Pane

   The MySQL Installation Package includes a MySQL preference
   Pane that enables you to start, stop, and control automated
   startup during boot of your MySQL installation.

   To install the MySQL Preference Pane:

    1. Download and open the MySQL package installer, which is
       provided on a disk image (.dmg) that includes the main
       MySQL installation package.
       Note
       Previously, the OS X packages included separate
       MySQLStartupItem.pkg and MySQL.prefPane files. They have
       since been merged into the main package file.
       Figure 2.48 MySQL Package Installer: DMG Contents
       MySQL Package Installer: DMG Contents

    2. Go through the process of installing the MySQL server, as
       described in the documentation at Section 2.4.2,
       "Installing MySQL on OS X Using Native Packages."

    3. Click Customize at the Installation Type step. The
       "Preference Pane" option is listed there and enabled by
       default.
       Figure 2.49 MySQL Installer on OS X: Customize
       MySQL Installer on OS X: Customize

    4. Complete the MySQL server installation process.

   Note

   The MySQL Preference Pane only starts and stops MySQL
   installation installed from the MySQL package installation
   that have been installed in the default location.

   Once the MySQL Preference Pane has been installed, you can
   control your MySQL server instance using the preference pane.
   To use the preference pane, open the System Preferences...
   from the Apple menu. Select the MySQL preference pane by
   clicking the MySQL logo within the bottom section of the
   preference panes list.

   Figure 2.50 MySQL Preference Pane: Location
   MySQL Preference Pane: Location

   The MySQL Preference Pane shows the current status of the
   MySQL server, showing stopped (in red) if the server is not
   running and running (in green) if the server has already been
   started. The preference pane also shows the current setting
   for whether the MySQL server has been set to start
   automatically.

     * To start the MySQL server using the preference pane:
       Click Start MySQL Server. You may be prompted for the
       username and password of a user with administrator
       privileges to start the MySQL server.

     * To stop the MySQL server using the preference pane:
       Click Stop MySQL Server. You may be prompted for the
       username and password of a user with administrator
       privileges to stop the MySQL server.

     * To automatically start the MySQL server when the system
       boots:
       Check the check box next to Automatically Start MySQL
       Server on Startup.

     * To disable automatic MySQL server startup when the system
       boots:
       Uncheck the check box next to Automatically Start MySQL
       Server on Startup.

   You can close the System Preferences... window once you have
   completed your settings.
