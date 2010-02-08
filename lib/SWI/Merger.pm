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

use strict;
use FileHandle;
use XML::Simple;

#
# Export section
#
require Exporter;
use vars qw($VERSION @ISA @EXPORT @EXPORT_OK $PREFERRED_PARSER);
@ISA              = qw(Exporter);
@EXPORT           = qw(swiMerge);
@EXPORT_OK        = qw();
$VERSION          = '1.0';
$PREFERRED_PARSER = undef;

#
# Enter point
#
sub swiMerge
{
    my $config         = shift();
    
    my $reportLocation =
        $config->{"swi:report"}->{"swi:destination"} . "/"
      . $config->{"swi:report"}->{"swi:xml"}->{"swi:name"};

    my $fh = new FileHandle( $reportLocation . ".x", "w" ) or die ("Can not open output file '$reportLocation'!");

    print $fh "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n";
    print $fh "<swi:report>\n";
    print $fh "\n";
    print $fh "  <swi:info>\n";
    print $fh "    <swi:version>1.0</swi:version>\n";
    if (defined($ENV{USER}))
    {
        print $fh "    <swi:user>" . $ENV{USER} . "</swi:user>\n";
    }
    print $fh "    <swi:generator>SWI/MERGER</swi:generator>\n";
    print $fh "  </swi:info>\n";
    print $fh "\n";
    
    my $modulesCount = $#{ $config->{"swi:modules"}->{"swi:module"} } + 1;
    my $filesCount = 0;
    my $functionsCount = 0;

    for ( my $i = 0 ; $i < $modulesCount ; $i++ )
    {
        my $modFh = new FileHandle( "$reportLocation.$i", "r" ) or die ("Can not open input file '$reportLocation.$i'!");
        my @lines = <$modFh>;
        $modFh->close();
        for ( my $j = 3 ; $j < $#lines ; $j++ )
        {
            print $fh $lines[$j];
            if ($lines[$j] =~ m/^[ ]*<swi:count>[ ]*$/)
            {
                if ($lines[$j+1] =~ m/^[ ]*<swi:files[ ]+swi:exact="([0-9]*)"[ ]*\/>[ ]*$/)
                {
                    my $numFilesInModule = $1;
                    if ($lines[$j+2] =~ m/^[ ]*<swi:functions[ ]+swi:exact="([0-9]*)"[ ]*\/>[ ]*$/)
                    {
                        my $numFunctionsInModule = $1;
                        $functionsCount += $numFunctionsInModule;
                        $filesCount += $numFilesInModule;
                    }
                }
            }
        }
    }

    print $fh "  <swi:statistic>\n";
    print $fh "    <swi:count>\n";
    print $fh "      <swi:modules swi:exact=\"" . $modulesCount . "\" />\n";
    print $fh "      <swi:files swi:exact=\"" . $filesCount . "\" />\n";
    print $fh "      <swi:functions swi:exact=\"" . $functionsCount . "\" />\n";
    print $fh "    </swi:count>\n";
    print $fh "  </swi:statistic>\n";
    print $fh "\n";

    print $fh "</swi:report>\n";
    
    $fh->close();

    return 0;
}

return 1;