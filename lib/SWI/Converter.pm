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
use XML::Simple;
use FileHandle;
use Data::Dumper;

#
# Export section
#
require Exporter;
use vars qw($VERSION @ISA @EXPORT @EXPORT_OK $PREFERRED_PARSER);
@ISA              = qw(Exporter);
@EXPORT           = qw(swiConvert);
@EXPORT_OK        = qw();
$VERSION          = '1.0';
$PREFERRED_PARSER = undef;

#
# Global variables
#
my $config = undef;

#
# Enter point
#
sub swiConvert
{
    $config = shift();

    my $report   = undef;
    my $exitCode = 0;

    $report = XMLin(
        $config->{"swi:report"}->{"swi:destination"} . "/"
          . $config->{"swi:report"}->{"swi:xml"}->{"swi:name"},
        ForceArray =>
          [ "swi:module", "swi:file", "swi:function", "swi:reference" ]
    );

    # generate notification report
    my $fh = new FileHandle(
        $config->{"swi:report"}->{"swi:destination"} . "/"
          . $config->{"swi:report"}->{"swi:notifications"}->{"swi:name"},
        "w"
      )
      or die("Can not open output file!");

    if ( defined( $ENV{USER} ) )
    {
        print $fh "User\t" . $ENV{USER} . "\n";
    }
    print $fh "\n";

    my $projectStat     = $report->{"swi:statistic"};
    my $projectName     = $config->{"swi:info"}->{"swi:project"}->{"swi:name"};
    my $projectLocation = $config->{"swi:report"}->{"swi:destination"};
    my $projectDiff     = "modified";
    $exitCode +=
      swiNotificationPrint( $fh, $projectName, $projectLocation, undef,
        $projectStat, $projectDiff );
    for (
        my $moduleId = 0 ;
        $moduleId <= $#{ $report->{"swi:module"} } ;
        $moduleId++
      )
    {
        my $moduleStat = $report->{"swi:module"}[$moduleId]->{"swi:statistic"};
        my $moduleName = $report->{"swi:module"}[$moduleId]->{"swi:name"};
        my $moduleLocation =
          $report->{"swi:module"}[$moduleId]->{"swi:location"};
        my $moduleDiff =
          $report->{"swi:module"}[$moduleId]->{"swi:modification"};
        $exitCode +=
          swiNotificationPrint( $fh, $projectName . "/" . $moduleName,
            $moduleLocation, undef, $moduleStat, $moduleDiff );
        for (
            my $fileId = 0 ;
            $fileId <= $#{ $report->{"swi:module"}[$moduleId]->{"swi:file"} } ;
            $fileId++
          )
        {
            my $fileStat =
              $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
              ->{"swi:statistic"};
            my $fileName =
              $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
              ->{"swi:name"};
            my $fileLocation =
              $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
              ->{"swi:location"};
            my $fileDiff =
              $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
              ->{"swi:modification"};
            $exitCode += swiNotificationPrint(
                $fh, $projectName . "/" . $moduleName . "/" . $fileName,
                $moduleLocation, $fileLocation . ":0",
                $fileStat, $fileDiff
            );
            for (
                my $functionId = 0 ;
                $functionId <= $#{
                    $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                      ->{"swi:function"}
                } ;
                $functionId++
              )
            {
                my $functionRefs =
                  $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                  ->{"swi:function"}[$functionId]->{"swi:reference"};
                my $functionStat =
                  $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                  ->{"swi:function"}[$functionId]->{"swi:statistic"};
                my $functionName =
                  $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                  ->{"swi:function"}[$functionId]->{"swi:name"};
                my $functionLocation =
                  $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                  ->{"swi:function"}[$functionId]->{"swi:location"};
                my $functionDiff =
                  $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                  ->{"swi:function"}[$functionId]->{"swi:modification"};
                $exitCode += swiNotificationPrint(
                    $fh,
                    $projectName . "/"
                      . $moduleName . "/"
                      . $fileName . "/"
                      . $functionName,
                    $moduleLocation,
                    $functionLocation,
                    $functionStat,
                    $functionDiff,
                    $functionRefs
                );
            }
        }
    }
    $fh->close();

    $fh = new FileHandle(
        $config->{"swi:report"}->{"swi:destination"} . "/"
          . $config->{"swi:report"}->{"swi:notifications"}->{"swi:name"},
        "r"
      )
      or die("Can not open input file!");

    while (<$fh>)
    {
        print STDERR $_;
    }
    $fh->close();

    return $exitCode;
}

sub swiNotificationPrint
{
    my $file         = shift();
    my $objName      = shift();
    my $modLocation  = shift();
    my $fileLocation = shift();
    my $objStat      = shift();
    my $objDiff      = shift();
    my $objRefs      = shift();
    my $returnCode   = 0;

    if ( !defined($fileLocation) )
    {
        $fileLocation = ".";
    }

    # Print 'swi:modifications'
    if (   $objDiff ne "unmodified"
        && $config->{"swi:report"}->{"swi:notifications"}->{"swi:print"}
        ->{ "swi:" . $objDiff }->{"swi:modifications"} eq "on" )
    {
        my $notification =
            "$modLocation/$fileLocation: " . "info"
          . ": Object "
          . $objName
          . " has been "
          . $objDiff
          . "\n\tObject         : "
          . $objName . "\n";
        print $file $notification;
        print $file "\n";
    }

    # Print 'swi:failures'
    foreach my $keyStat ( keys %$objStat )
    {
        my $subStat = $objStat->{$keyStat};
        foreach my $keySubStat ( keys %$subStat )
        {
            my $types = $objStat->{$keyStat}->{$keySubStat};
            foreach my $type ( keys %$types )
            {
                my $statInfo = $objStat->{$keyStat}->{$keySubStat}->{$type};
                if (
                    !(
                        $statInfo->{"swi:level"} eq $statInfo->{"swi:suppress"}
                        || (   $statInfo->{"swi:level"} eq "regular"
                            && $statInfo->{"swi:suppress"} eq "undefined" )
                    )
                  )
                {
                    my $notification =
                        "$modLocation/$fileLocation: "
                      . $statInfo->{"swi:level"}
                      . ": Index '"
                      . "$keyStat/$keySubStat/$type"
                      . "' exceeds the limit"
                      . "\n\tObject         : "
                      . $objName
                      . "\n\tIndex value    : "
                      . $statInfo->{"content"}
                      . "\n\tModification   : "
                      . $objDiff . " / "
                      . $statInfo->{"swi:change"}
                      . "\n\tSeverity       : "
                      . $statInfo->{"swi:level"}
                      . "\n\tCriteria       : "
                      . $statInfo->{"swi:criteria"}
                      . "\n\tSuppress level : "
                      . $statInfo->{"swi:suppress"} . "\n";

                    if ( $config->{"swi:report"}->{"swi:notifications"}
                        ->{"swi:print"}->{ "swi:" . $objDiff }->{"swi:failures"}
                        eq "on" )
                    {
                        print $file $notification;

                        # Print 'swi:duplications'
                        if (   $keyStat eq "swi:duplication"
                            && $keySubStat eq "swi:symbols"
                            && $config->{"swi:report"}->{"swi:notifications"}
                            ->{"swi:print"}->{ "swi:" . $objDiff }
                            ->{"swi:duplications"} eq "on" )
                        {
                            die('Internal Error occured!')
                              if not defined($objRefs);
                            print $file "\n";
                            foreach my $dupData ( @{$objRefs} )
                            {
                                if ( $dupData->{'swi:ref:type'} eq 'dup' )
                                {
                                    print $file $modLocation . "/"
                                      . $dupData->{'swi:dup:file'} . ":"
                                      . $dupData->{'swi:dup:line'}
                                      . ": warning: '"
                                      . $dupData->{'swi:dup:size'}
                                      . "' executable symbols are duplicated in '"
                                      . $dupData->{'swi:dup:function'}
                                      . "' function\n";
                                }
                            }
                        }
                        print $file "\n";
                    }

                    if ( $config->{"swi:report"}->{"swi:notifications"}
                        ->{"swi:error"}->{ "swi:" . $objDiff } eq "on" )
                    {
                        $returnCode++;
                    }
                }
                if (   $statInfo->{"swi:level"} eq "unresolved"
                    || $statInfo->{"swi:suppress"} eq "unresolved" )
                {
                    my $notification =
                        "$modLocation/$fileLocation: "
                      . $statInfo->{"swi:level"}
                      . ": The level/severity of index '"
                      . "$keyStat/$keySubStat/$type"
                      . "' is unresolved"
                      . "\n\tObject         : "
                      . $objName
                      . "\n\tIndex value    : "
                      . $statInfo->{"content"}
                      . "\n\tModification   : "
                      . $objDiff . " / "
                      . $statInfo->{"swi:change"}
                      . "\n\tSeverity       : "
                      . $statInfo->{"swi:level"}
                      . "\n\tCriteria       : "
                      . $statInfo->{"swi:criteria"}
                      . "\n\tSuppress level : "
                      . $statInfo->{"swi:suppress"} . "\n\n";

                    print $file $notification;
                    $returnCode++;
                }
            }
        }
    }

    # Print 'swi:scanmessages'
    if ( $config->{"swi:report"}->{"swi:notifications"}->{"swi:print"}
        ->{ "swi:" . $objDiff }->{"swi:scanmessages"} eq "on" )
    {
        foreach my $scanData ( @{$objRefs} )
        {
            if ( $scanData->{'swi:ref:type'} eq 'scan' )
            {
                print $file $modLocation . "/"
                  . $scanData->{'swi:scan:file'} . ":"
                  . $scanData->{'swi:scan:line'}
                  . ": warning: '"
                  . $scanData->{'swi:scan:message'}
                  . "\n\tObject         : "
                  . $objName
                  . "\n\tModification   : "
                  . $objDiff . "\n\n";
                $returnCode++;
            }
        }
    }

    return $returnCode;
}

return 1;
