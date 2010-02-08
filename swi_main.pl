#!/usr/bin/perl
#
#    Software Index, Copyright 2010, Software Index Project Team
#    Link: http://swi.sourceforge.net
#
#    This file is part of Software Index Tool.
#
#    Software Index is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    Software Index is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Software Index.  If not, see <http://www.gnu.org/licenses/>.
#

=head1 NAME

Software Index - the tool measures, reports and validates software statistic,
searches for duplications, scans for errors, 'coding style' violations
and other configurable patterns.

=head1 SYNOPSIS

    perl swi_main.pl -h
    perl swi_main.pl -help
    perl swi_main.pl --help
    
    perl swi_main.pl </path/to/configuration/file.xml>

=head1 OPTIONS

=over 4

=item -h, -help, --help

Prints this help page.

=item </path/to/configuration/file.xml>

Full or relative path to the configuration file for the tool. Configuration file
should include the predefined set of XML sections and tags. Use swi_config_sample.xml file
(from the distributable package) as a 'configration file description'
and create new configs using this file as a baseline. The sample explains every
section in details and gives several usage examples.

=back

=head1 ENVIRONMENT

The tool requires Perl Runtime Environment. Required Perl version is 5.6.x or later.

=head1 INSTALLATION

In order to install the distributive, unpack the distributable package to some folder.

Software Index has internal tool (dupindex) which should be compiled for the target platform.
By default, the distributable archive includes the compiled binary for PC Windows platform.
Recompile it if you need (only one file dupindex.cpp), using g++ or some other C++ compiler.
There is a project configuration file for users of Microsoft Visual Studio 2008.  

=head1 COPYRIGHT 

Software Index, Copyright 2009, 2010, Software Index Project Team,
Link: http://swi.sourceforge.net

=head1 LICENSE

Software Index is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

Software Index is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Software Index.  If not, see <http://www.gnu.org/licenses/>.

=cut




use strict;
use Cwd qw(abs_path);
use Pod::Usage;

$0 =~ m/(.*)swi_main.pl$/;
my $globalRootDirectory      = abs_path($1);

push(@INC, "$globalRootDirectory/lib");
require SWI::Launcher;

if (!defined($ARGV[0]) || $ARGV[0] eq "-help" || $ARGV[0] eq "--help" || $ARGV[0] eq "-h")
{
    pod2usage(-exitstatus => 0, -verbose => 2);    
}

exit swiLaunch($globalRootDirectory, @ARGV);
