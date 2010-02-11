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

=head1 OVERVIEW

Software Index measures, reports and validates software statistic,
searches for duplications, scans for errors, 'coding style' violations
and occasions of broken design patterns which are defined by your design team. 

=head1 SYNOPSIS

In order to get the context help (this text):

    perl swi_main.pl -h
    perl swi_main.pl -help
    perl swi_main.pl --help
    
In order to get the sample configuration file and it's description:

    perl swi_main.pl -s
    perl swi_main.pl -sample
    perl swi_main.pl --sample

In order to launch the tool with the prepared configuration file:

    perl swi_main.pl </path/to/configuration/file.xml>

=head1 OPTIONS

=over 4

=item -h, -help, --help

Prints this help page.

=item -s, -sample, --sample

Prints the example of configuration file and it's description.
The sample explains every section in details and gives several usage examples.
Use this as a start up framework for your initial configs.
For example:

    > perl swi_main.pl -sample > my_config.xml

=item </path/to/configuration/file.xml>

Full or relative path to the configuration file for the tool. 

=back

=head1 ENVIRONMENT

The tool requires Perl Runtime Environment. Required Perl version is 5.6.x or later.

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
my $globalRootDirectory = abs_path($1);

push( @INC, "$globalRootDirectory/lib" );
require SWI::Launcher;

if (   !defined( $ARGV[0] )
    || $ARGV[0] eq "-help"
    || $ARGV[0] eq "--help"
    || $ARGV[0] eq "-h" )
{
    pod2usage( -exitstatus => 0, -verbose => 2 );
    exit 0;
}

if (   $ARGV[0] eq "-sample"
    || $ARGV[0] eq "--sample"
    || $ARGV[0] eq "-s" )
{
    my $fh = new FileHandle( "$globalRootDirectory/swi_config_sample.xml", "r" )
      or die(
        "Can not open input file '$globalRootDirectory/swi_config_sample.xml'!"
      );

    while (<$fh>)
    {
        print $_;
    }
    exit 0;
}

exit swiLaunch( $globalRootDirectory, @ARGV );
