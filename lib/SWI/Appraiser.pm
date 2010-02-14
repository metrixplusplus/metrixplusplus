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
use Internal::Output;
use FileHandle;
use Data::Dumper;

#
# Export section
#
require Exporter;
use vars qw($VERSION @ISA @EXPORT @EXPORT_OK $PREFERRED_PARSER);
@ISA              = qw(Exporter);
@EXPORT           = qw(swiAppraise);
@EXPORT_OK        = qw();
$VERSION          = '1.0';
$PREFERRED_PARSER = undef;

#
# Subroutine for troubleshooting purposes
#
use Internal::Output;

#
# Global variables
#
my $config = undef;
my $report = undef;

#
# Enter point
#
sub swiAppraise
{
    $config = shift();

    my $reportBase = undef;

    $report = XMLin(
        $config->{"swi:report"}->{"swi:destination"} . "/"
          . $config->{"swi:report"}->{"swi:xml"}->{"swi:name"} . ".x",
        ForceArray =>
          [ "swi:module", "swi:file", "swi:function", "swi:reference" ]
    );

    if ( defined( $config->{"swi:report"}->{"swi:xml"}->{"swi:baseline"} )
        && $config->{"swi:report"}->{"swi:xml"}->{"swi:baseline"} ne "" )
    {
        $reportBase = XMLin(
            $config->{"swi:report"}->{"swi:destination"} . "/"
              . $config->{"swi:report"}->{"swi:xml"}->{"swi:baseline"},
            ForceArray =>
              [ "swi:module", "swi:file", "swi:function", "swi:reference" ]
        );
    }

    my $projectStat = $report->{"swi:statistic"};
    for (
        my $moduleId = 0 ;
        $moduleId <= $#{ $report->{"swi:module"} } ;
        $moduleId++
      )
    {
        my $moduleStat = $report->{"swi:module"}[$moduleId]->{"swi:statistic"};
        for (
            my $fileId = 0 ;
            $fileId <= $#{ $report->{"swi:module"}[$moduleId]->{"swi:file"} } ;
            $fileId++
          )
        {
            my $fileStat =
              $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
              ->{"swi:statistic"};
            for (
                my $functionId = 0 ;
                $functionId <= $#{
                    $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                      ->{"swi:function"}
                } ;
                $functionId++
              )
            {
                my $functionStat =
                  $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                  ->{"swi:function"}[$functionId]->{"swi:statistic"};

                foreach my $keyStat ( keys %$functionStat )
                {
                    my $subStat = $functionStat->{$keyStat};
                    foreach my $keySubStat ( keys %$subStat )
                    {

                        # add total per file
                        $fileStat->{$keyStat}->{$keySubStat}->{"swi:total"} +=
                          $subStat->{$keySubStat}->{'swi:exact'};
                        $fileStat->{$keyStat}->{$keySubStat}->{"swi:average"} =
                          $fileStat->{$keyStat}->{$keySubStat}->{"swi:total"} /
                          $fileStat->{"swi:count"}->{"swi:functions"}
                          ->{'swi:exact'};

                        # add total per module
                        $moduleStat->{$keyStat}->{$keySubStat}->{"swi:total"} +=
                          $subStat->{$keySubStat}->{'swi:exact'};
                        $moduleStat->{$keyStat}->{$keySubStat}
                          ->{"swi:average"} =
                          $moduleStat->{$keyStat}->{$keySubStat}
                          ->{"swi:total"} /
                          $moduleStat->{"swi:count"}->{"swi:functions"}
                          ->{'swi:exact'};

                        # add total per project
                        $projectStat->{$keyStat}->{$keySubStat}
                          ->{"swi:total"} +=
                          $subStat->{$keySubStat}->{'swi:exact'};
                        $projectStat->{$keyStat}->{$keySubStat}
                          ->{"swi:average"} =
                          $projectStat->{$keyStat}->{$keySubStat}
                          ->{"swi:total"} /
                          $projectStat->{"swi:count"}->{"swi:functions"}
                          ->{'swi:exact'};

                        # add minimum per file
                        if (
                            !defined(
                                $fileStat->{$keyStat}->{$keySubStat}
                                  ->{"swi:min"}
                            )
                            || $fileStat->{$keyStat}->{$keySubStat}
                            ->{"swi:min"} >
                            $subStat->{$keySubStat}->{'swi:exact'}
                          )
                        {
                            $fileStat->{$keyStat}->{$keySubStat}->{"swi:min"} =
                              $subStat->{$keySubStat}->{'swi:exact'};
                        }

                        # add minimum per module
                        if (
                            !defined(
                                $moduleStat->{$keyStat}->{$keySubStat}
                                  ->{"swi:min"}
                            )
                            || $moduleStat->{$keyStat}->{$keySubStat}
                            ->{"swi:min"} >
                            $subStat->{$keySubStat}->{'swi:exact'}
                          )
                        {
                            $moduleStat->{$keyStat}->{$keySubStat}
                              ->{"swi:min"} =
                              $subStat->{$keySubStat}->{'swi:exact'};
                        }

                        # add minimum per project
                        if (
                            !defined(
                                $projectStat->{$keyStat}->{$keySubStat}
                                  ->{"swi:min"}
                            )
                            || $projectStat->{$keyStat}->{$keySubStat}
                            ->{"swi:min"} >
                            $subStat->{$keySubStat}->{'swi:exact'}
                          )
                        {
                            $projectStat->{$keyStat}->{$keySubStat}
                              ->{"swi:min"} =
                              $subStat->{$keySubStat}->{'swi:exact'};
                        }

                        # add maximum per file
                        if (
                            !defined(
                                $fileStat->{$keyStat}->{$keySubStat}
                                  ->{"swi:max"}
                            )
                            || $fileStat->{$keyStat}->{$keySubStat}
                            ->{"swi:max"} <
                            $subStat->{$keySubStat}->{'swi:exact'}
                          )
                        {
                            $fileStat->{$keyStat}->{$keySubStat}->{"swi:max"} =
                              $subStat->{$keySubStat}->{'swi:exact'};
                        }

                        # add maximum per module
                        if (
                            !defined(
                                $moduleStat->{$keyStat}->{$keySubStat}
                                  ->{"swi:max"}
                            )
                            || $moduleStat->{$keyStat}->{$keySubStat}
                            ->{"swi:max"} <
                            $subStat->{$keySubStat}->{'swi:exact'}
                          )
                        {
                            $moduleStat->{$keyStat}->{$keySubStat}
                              ->{"swi:max"} =
                              $subStat->{$keySubStat}->{'swi:exact'};
                        }

                        # add maximum per project
                        if (
                            !defined(
                                $projectStat->{$keyStat}->{$keySubStat}
                                  ->{"swi:max"}
                            )
                            || $projectStat->{$keyStat}->{$keySubStat}
                            ->{"swi:max"} <
                            $subStat->{$keySubStat}->{'swi:exact'}
                          )
                        {
                            $projectStat->{$keyStat}->{$keySubStat}
                              ->{"swi:max"} =
                              $subStat->{$keySubStat}->{'swi:exact'};
                        }
                    }
                }
            }
        }
    }

    # generate full XML report
    my $outputFile =
        $config->{"swi:report"}->{"swi:destination"} . "/"
      . $config->{"swi:report"}->{"swi:xml"}->{"swi:name"};
    my $fh = new FileHandle( $outputFile, "w" )
      or die("Can not open output file '$outputFile'!");

    print $fh "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n";
    print $fh "<swi:report>\n";
    print $fh "\n";

    print $fh "  <swi:info>\n";
    print $fh "    <swi:version>1.0</swi:version>\n";
    if ( defined( $ENV{USER} ) )
    {
        print $fh "    <swi:user>" . $ENV{USER} . "</swi:user>\n";
    }
    print $fh "    <swi:generator>SWI/APPRAISER</swi:generator>\n";
    print $fh "  </swi:info>\n";
    print $fh "\n";

    $projectStat = $report->{"swi:statistic"};
    my $projectName = $config->{"swi:info"}->{"swi:project"}->{"swi:name"};
    my $projectDiff =
      swiReportModificationGet( $reportBase, $report, "swi:total" );
    for (
        my $moduleId = 0 ;
        $moduleId <= $#{ $report->{"swi:module"} } ;
        $moduleId++
      )
    {
        my $moduleStat = $report->{"swi:module"}[$moduleId]->{"swi:statistic"};
        my $moduleName = $report->{"swi:module"}[$moduleId]->{"swi:name"};
        my $moduleBase =
          swiReportObjectFind( $reportBase->{"swi:module"}, $moduleName );
        my $moduleDiff =
          swiReportModificationGet( $moduleBase,
            $report->{"swi:module"}[$moduleId], "swi:total" );
        print $fh "  <swi:module>\n";
        print $fh "    <swi:name>" . $moduleName . "</swi:name>\n";
        print $fh "    <swi:location>"
          . $report->{"swi:module"}[$moduleId]->{"swi:location"}
          . "</swi:location>\n";
        print $fh "    <swi:modification>"
          . $moduleDiff
          . "</swi:modification>\n";
        print $fh "\n";

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
            my $fileBase =
              ( $moduleDiff eq "added" )
              ? undef
              : swiReportObjectFind( $moduleBase->{"swi:file"}, $fileName );
            my $fileDiff =
              swiReportModificationGet( $fileBase,
                $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId],
                "swi:total" );
            print $fh "    <swi:file>\n";
            print $fh "      <swi:name>" . $fileName . "</swi:name>\n";
            print $fh "      <swi:location>"
              . $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
              ->{"swi:location"} . "</swi:location>\n";
            print $fh "      <swi:modification>"
              . $fileDiff
              . "</swi:modification>\n";
            print $fh "\n";

            for (
                my $functionId = 0 ;
                $functionId <= $#{
                    $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                      ->{"swi:function"}
                } ;
                $functionId++
              )
            {
                my $functionStat =
                  $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                  ->{"swi:function"}[$functionId]->{"swi:statistic"};
                my $functionName =
                  $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                  ->{"swi:function"}[$functionId]->{"swi:name"};
                my $functionBase =
                  ( $fileDiff eq "added" )
                  ? undef
                  : swiReportObjectFind( $fileBase->{"swi:function"},
                    $functionName );
                my $functionDiff = swiReportModificationGet(
                    $functionBase,
                    $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                      ->{"swi:function"}[$functionId],
                    "swi:exact"
                );
                print $fh "      <swi:function>\n";
                print $fh "        "
                  . XMLout( $functionName, RootName => 'swi:name' );
                print $fh "        "
                  . XMLout(
                    $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                      ->{"swi:function"}[$functionId]->{"swi:location"},
                    RootName => 'swi:location'
                  );
                print $fh "        "
                  . XMLout(
                    $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                      ->{"swi:function"}[$functionId]->{"swi:modifier"},
                    RootName => 'swi:modifier'
                  );
                print $fh "        "
                  . XMLout(
                    $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                      ->{"swi:function"}[$functionId]->{"swi:pointer"},
                    RootName => 'swi:pointer'
                  );
                print $fh "        <swi:modification>"
                  . $functionDiff
                  . "</swi:modification>\n";
                print $fh "        <swi:statistic>\n";

                foreach my $keyStat ( keys %$functionStat )
                {
                    print $fh "          <" . $keyStat . ">\n";
                    my $subStat = $functionStat->{$keyStat};
                    foreach my $keySubStat ( keys %$subStat )
                    {
                        my ( $level, $suppress, $criteria ) =
                          swiStatisticLevelGet(
                            $keyStat,
                            $keySubStat,
                            "swi:exact",
                            $projectName . "/"
                              . $moduleName . "/"
                              . $fileName . "/"
                              . $functionName,
                            $functionStat,
                            "swi:function"
                          );
                        my $statDiff = swiStatisticDiffGet(
                            $functionDiff,
                            $functionStat->{$keyStat}->{$keySubStat}
                              ->{'swi:exact'},
                            $functionBase->{"swi:statistic"}->{$keyStat}
                              ->{$keySubStat}->{"swi:exact"}->{'content'}
                        );
                        print $fh "            <"
                          . $keySubStat
                          . "><swi:exact swi:change=\""
                          . $statDiff
                          . "\" swi:level=\""
                          . $level
                          . "\" swi:suppress=\""
                          . $suppress
                          . "\" swi:criteria=\""
                          . $criteria . "\">"
                          . $functionStat->{$keyStat}->{$keySubStat}
                          ->{'swi:exact'}
                          . "</swi:exact></"
                          . $keySubStat . ">\n";
                    }
                    print $fh "          </" . $keyStat . ">\n";
                }
                print $fh "        </swi:statistic>\n";

                my $refers =
                  $report->{"swi:module"}[$moduleId]->{"swi:file"}[$fileId]
                  ->{"swi:function"}[$functionId]->{'swi:reference'};
                if ( defined($refers) )
                {
                    foreach my $refData ( @{$refers} )
                    {
                        if ( $refData->{'swi:ref:type'} eq 'scan' )
                        {
                            foreach my $pattern (
                                @{
                                    $config->{'swi:modules'}
                                      ->{"swi:module"}[$moduleId]
                                      ->{'swi:scanner'}->{'swi:suppress'}
                                      ->{'swi:pattern'}
                                }
                              )
                            {
                                my $msgPattern = $pattern->{'swi:message'};
                                my $objPattern = $pattern->{'content'};
                                if ( $refData->{'swi:scan:message'} =~
                                       m/$msgPattern/
                                    && "$projectName/$moduleName/$fileName/$functionName"
                                    =~ m/$objPattern/ )
                                {
                                    $refData->{'swi:scan:suppress'} = 'on';
                                    $pattern->{'swi:used'}          = 1;
                                    last;
                                }
                            }
                        }
                    }

                    my $refStr = XMLout( $refers, RootName => '' );
                    $refStr =~ s/\n/\n      /g;
                    $refStr =~ s/<anon /<swi:reference /g;
                    print $fh "      ";
                    print $fh $refStr;
                    print $fh "\n";
                }

                print $fh "      </swi:function>\n";
                print $fh "\n";
            }
            for (
                my $functionId = 0 ;
                $functionId <= $#{ $fileBase->{"swi:function"} } ;
                $functionId++
              )
            {
                my $functionOld = $fileBase->{"swi:function"}[$functionId];
                if (
                    swiReportObjectFind(
                        $report->{"swi:module"}[$moduleId]
                          ->{"swi:file"}[$fileId]->{"swi:function"},
                        $functionOld->{"swi:name"}
                    ) == undef
                  )
                {
                    print $fh "      <swi:function>\n";
                    print $fh "        <swi:name>"
                      . $functionOld->{"swi:name"}
                      . "</swi:name>\n";
                    print $fh "        <swi:location>"
                      . $functionOld->{"swi:location"}
                      . "</swi:location>\n";
                    print $fh
                      "        <swi:modification>removed</swi:modification>\n";
                    print $fh "      </swi:function>\n";
                    print $fh "\n";
                }
            }

            print $fh "      <swi:statistic>\n";
            foreach my $keyStat ( keys %$fileStat )
            {
                print $fh "        <" . $keyStat . ">\n";
                my $subStat = $fileStat->{$keyStat};
                foreach my $keySubStat ( keys %$subStat )
                {
                    my @types = (
                        "swi:exact", "swi:average",
                        "swi:min",   "swi:max",
                        "swi:total"
                    );
                    print $fh "          <" . $keySubStat . ">\n";
                    foreach my $type (@types)
                    {
                        if (
                            defined(
                                $fileStat->{$keyStat}->{$keySubStat}->{$type}
                            )
                          )
                        {
                            my ( $level, $suppress, $criteria ) =
                              swiStatisticLevelGet(
                                $keyStat,
                                $keySubStat,
                                $type,
                                $projectName . "/"
                                  . $moduleName . "/"
                                  . $fileName,
                                $fileStat,
                                "swi:file"
                              );
                            my $statDiff = swiStatisticDiffGet(
                                $fileDiff,
                                $fileStat->{$keyStat}->{$keySubStat}->{$type},
                                $fileBase->{"swi:statistic"}->{$keyStat}
                                  ->{$keySubStat}->{$type}->{'content'}

                            );
                            print $fh "            <" . $type
                              . " swi:change=\""
                              . $statDiff
                              . "\" swi:level=\""
                              . $level
                              . "\" swi:suppress=\""
                              . $suppress
                              . "\" swi:criteria=\""
                              . $criteria . "\">"
                              . sprintf( "%.2f",
                                $fileStat->{$keyStat}->{$keySubStat}->{$type} )
                              . "</"
                              . $type . ">\n";
                        }
                    }
                    print $fh "          </" . $keySubStat . ">\n";
                }
                print $fh "        </" . $keyStat . ">\n";
            }
            print $fh "      </swi:statistic>\n";
            print $fh "    </swi:file>\n";
            print $fh "\n";
        }
        for (
            my $fileId = 0 ;
            $fileId <= $#{ $moduleBase->{"swi:file"} } ;
            $fileId++
          )
        {
            my $fileOld = $moduleBase->{"swi:file"}[$fileId];
            if (
                swiReportObjectFind(
                    $report->{"swi:module"}[$moduleId]->{"swi:file"},
                    $fileOld->{"swi:name"} ) == undef
              )
            {
                print $fh "    <swi:file>\n";
                print $fh "      <swi:name>"
                  . $fileOld->{"swi:name"}
                  . "</swi:name>\n";
                print $fh "      <swi:location>"
                  . $fileOld->{"swi:location"}
                  . "</swi:location>\n";
                print $fh
                  "      <swi:modification>removed</swi:modification>\n";
                print $fh "    </swi:file>\n";
                print $fh "\n";
            }
        }

        print $fh "    <swi:statistic>\n";
        foreach my $keyStat ( keys %$moduleStat )
        {
            print $fh "      <" . $keyStat . ">\n";
            my $subStat = $moduleStat->{$keyStat};
            foreach my $keySubStat ( keys %$subStat )
            {
                my @types = (
                    "swi:exact", "swi:average", "swi:min", "swi:max",
                    "swi:total"
                );
                print $fh "        <" . $keySubStat . ">\n";
                foreach my $type (@types)
                {
                    if (
                        defined(
                            $moduleStat->{$keyStat}->{$keySubStat}->{$type}
                        )
                      )
                    {
                        my ( $level, $suppress, $criteria ) =
                          swiStatisticLevelGet( $keyStat, $keySubStat, $type,
                            $projectName . "/" . $moduleName,
                            $moduleStat, "swi:module" );
                        my $statDiff = swiStatisticDiffGet(
                            $moduleDiff,
                            $moduleStat->{$keyStat}->{$keySubStat}->{$type},
                            $moduleBase->{"swi:statistic"}->{$keyStat}
                              ->{$keySubStat}->{$type}->{'content'}

                        );
                        print $fh "          <" . $type
                          . " swi:change=\""
                          . $statDiff
                          . "\" swi:level=\""
                          . $level
                          . "\" swi:suppress=\""
                          . $suppress
                          . "\" swi:criteria=\""
                          . $criteria . "\">"
                          . sprintf( "%.2f",
                            $moduleStat->{$keyStat}->{$keySubStat}->{$type} )
                          . "</"
                          . $type . ">\n";
                    }
                }
                print $fh "        </" . $keySubStat . ">\n";

            }
            print $fh "      </" . $keyStat . ">\n";
        }
        print $fh "    </swi:statistic>\n";
        print $fh "  </swi:module>\n";
        print $fh "\n";
    }
    for (
        my $moduleId = 0 ;
        $moduleId <= $#{ $reportBase->{"swi:module"} } ;
        $moduleId++
      )
    {
        my $moduleOld = $reportBase->{"swi:module"}[$moduleId];
        if (
            swiReportObjectFind( $report->{"swi:module"},
                $moduleOld->{"swi:name"} ) == undef
          )
        {
            print $fh "  <swi:module>\n";
            print $fh "    <swi:name>"
              . $moduleOld->{"swi:name"}
              . "</swi:name>\n";
            print $fh "    <swi:location>"
              . $moduleOld->{"swi:location"}
              . "</swi:location>\n";
            print $fh "    <swi:modification>removed</swi:modification>\n";
            print $fh "  </swi:module>\n";
            print $fh "\n";
        }
    }
    print $fh "  <swi:statistic>\n";
    foreach my $keyStat ( keys %$projectStat )
    {
        print $fh "    <" . $keyStat . ">\n";
        my $subStat = $projectStat->{$keyStat};
        foreach my $keySubStat ( keys %$subStat )
        {
            my @types =
              ( "swi:exact", "swi:average", "swi:min", "swi:max", "swi:total" );
            print $fh "      <" . $keySubStat . ">\n";
            foreach my $type (@types)
            {
                if (
                    defined( $projectStat->{$keyStat}->{$keySubStat}->{$type} )
                  )
                {
                    my ( $level, $suppress, $criteria ) = swiStatisticLevelGet(
                        $keyStat,     $keySubStat,  $type,
                        $projectName, $projectStat, "swi:project"
                    );
                    my $statDiff = swiStatisticDiffGet(
                        $projectDiff,
                        $projectStat->{$keyStat}->{$keySubStat}->{$type},
                        $reportBase->{"swi:statistic"}->{$keyStat}
                          ->{$keySubStat}->{$type}->{'content'}

                    );
                    print $fh "        <" . $type
                      . " swi:change=\""
                      . $statDiff
                      . "\" swi:level=\""
                      . $level
                      . "\" swi:suppress=\""
                      . $suppress
                      . "\" swi:criteria=\""
                      . $criteria . "\">"
                      . sprintf( "%.2f",
                        $projectStat->{$keyStat}->{$keySubStat}->{$type} )
                      . "</"
                      . $type . ">\n";
                }
            }
            print $fh "      </" . $keySubStat . ">\n";
        }
        print $fh "    </" . $keyStat . ">\n";
    }
    print $fh "  </swi:statistic>\n";
    print $fh "</swi:report>\n";

    swiCheckUselessPatterns($config);

    return 0;
}

sub swiStatisticLevelGet
{
    my $keyStat    = shift();
    my $keySubStat = shift();
    my $type       = shift();
    my $objName    = shift();
    my $objStat    = shift();
    my $objType    = shift();
    my $statValue  = undef;

    # Array of results: level, suppress level, criteria
    my @returnResult = ( "undefined", "undefined", "" );

    if (
        defined( $config->{"swi:limits"}->{$keyStat}->{$keySubStat}->{$type} ) )
    {
        my $limit = $config->{"swi:limits"}->{$keyStat}->{$keySubStat}->{$type};

        my $objectPattern = $limit->{"swi:objectpattern"};
        if ( defined($objectPattern) && $objName !~ m/$objectPattern/ )
        {
            $returnResult[2] = '[limit not applied]';
        }
        else
        {
            if ( defined( $limit->{"swi:relation"} ) )
            {
                my @relation = undef;
                @relation = split( /\//, $limit->{"swi:relation"} );

                my $factor =
                  $objStat->{ $relation[0] }->{ $relation[1] }
                  ->{ $relation[2] };

                if ( !defined($factor) || $factor == 0 )
                {
                    STATUS(
"Wrong configuration for the limit '$keyStat/$keySubStat/$type'. Relation "
                          . $limit->{"swi:relation"}
                          . " is not found for the object '$objName'"
                    );
                    $factor = 0;
                }
                if ($factor == 0)
                {
                    # Devide zero by zero, equals to 1
                    if ($objStat->{$keyStat}->{$keySubStat}->{$type} == 0)
                    {
                        $statValue = "1.00";
                    }
                    # Devide negative number by zero, equals to -infinity
                    elsif ($objStat->{$keyStat}->{$keySubStat}->{$type} < 0)
                    {
                        $statValue = "-Infinity";        
                    }
                    # Devide positive number by zero, equals to infinity
                    else
                    {
                        $statValue = "Infinity";
                    }
                }
                else
                {
                    $statValue = $objStat->{$keyStat}->{$keySubStat}->{$type} / $factor;
                    $statValue = sprintf( "%.2f", $statValue );
                }
            }
            else
            {
                $statValue = sprintf( "%.2f", $objStat->{$keyStat}->{$keySubStat}->{$type} );
            }

            if (   $limit->{"swi:warning"} > $limit->{"swi:notice"}
                && $limit->{"swi:notice"} > $limit->{"swi:info"} )
            {
                if ( $statValue eq "Infinity" || $statValue > $limit->{"swi:warning"} )
                {
                    $returnResult[0] = "warning";
                    $returnResult[2] = "["
                      . $statValue
                      . " greater than "
                      . $limit->{"swi:warning"} . "]";
                }
                elsif ( $statValue > $limit->{"swi:notice"} )
                {
                    $returnResult[0] = "notice";
                    $returnResult[2] = "["
                      . $statValue
                      . " greater than "
                      . $limit->{"swi:notice"} . "]";
                }
                elsif ( $statValue > $limit->{"swi:info"} )
                {
                    $returnResult[0] = "info";
                    $returnResult[2] = "["
                      . $statValue
                      . " greater than "
                      . $limit->{"swi:info"} . "]";
                }
                else
                {
                    $returnResult[0] = "regular";
                }
            }
            elsif ($limit->{"swi:warning"} < $limit->{"swi:notice"}
                && $limit->{"swi:notice"} < $limit->{"swi:info"} )
            {
                if ( $statValue eq "-Infinity" || $statValue < $limit->{"swi:warning"} )
                {
                    $returnResult[0] = "warning";
                    $returnResult[2] = "["
                      . $statValue
                      . " less than "
                      . $limit->{"swi:warning"} . "]";
                }
                elsif ( $statValue < $limit->{"swi:notice"} )
                {
                    $returnResult[0] = "notice";
                    $returnResult[2] = "["
                      . $statValue
                      . " less than "
                      . $limit->{"swi:notice"} . "]";
                }
                elsif ( $statValue < $limit->{"swi:info"} )
                {
                    $returnResult[0] = "info";
                    $returnResult[2] = "["
                      . $statValue
                      . " less than "
                      . $limit->{"swi:info"} . "]";
                }
                else
                {
                    $returnResult[0] = "regular";
                }
            }
            else
            {
                STATUS(
"Wrong settings in configuration file (swi:limits section): swi:limit/$keyStat/$keySubStat/$type"
                );
                $returnResult[0] = "unresolved";
            }

            # check if suppressed
            my $isFound = 0;

          LOOPPATTERNS:
            foreach ( @{ $limit->{"swi:suppress"}->{"swi:pattern"} } )
            {
                my $pattern = $_;
                if ( ref($pattern) eq "HASH"
                    && defined( $pattern->{"swi:level"} ) )
                {
                    my $content = $pattern->{"content"};
                    if ( $objName =~ m/$content/ )
                    {
                        if ( $isFound == 0 )
                        {
                            $returnResult[1]       = $pattern->{"swi:level"};
                            $pattern->{'swi:used'} = 1;
                            $isFound               = 1;
                        }
                        else
                        {

                            # This object is matched by several patterns
                            if ( $returnResult[1] ne $pattern->{"swi:level"} )
                            {

                                # and levels are not equal in different patterns
                                STATUS(
"Configuration is wrong: $objName is matched by several patterns"
                                );
                                $returnResult[1] = "unresolved";
                            }
                        }
                    }
                }
                else
                {
                    STATUS(
"Wrong settings in configuration file (swi:limits section): swi:limits/$keyStat/$keySubStat/$type: "
                          . "Level is missed in pattern for the object '$objType'"
                    );
                    $returnResult[1] = "unresolved";
                    $returnResult[2] = "[]";
                }
            }
        }
    }

    return @returnResult;
}

sub swiStatisticDiffGet
{
    my $objDiff = shift();
    my $newStat = shift();
    my $oldStat = shift();
    if ( $objDiff ne "added" )
    {
        return sprintf( "%.2f", $newStat - $oldStat );
    }
    return "";
}

sub swiReportObjectFind
{
    my $objects = shift();
    my $objName = shift();

    foreach (@$objects)
    {
        if (   $_->{"swi:name"} eq $objName
            && $_->{"swi:modification"} ne "removed" )
        {
            return $_;
        }
    }

    return undef;
}

sub swiReportModificationGet
{
    my $objBase  = shift();
    my $objNew   = shift();
    my $statType = shift();

    if ( !defined($objBase) )
    {
        return "added";
    }

    my $newCrc =
      $objNew->{"swi:statistic"}->{"swi:checksum"}->{"swi:source"}->{$statType};
    my $newLength =
      $objNew->{"swi:statistic"}->{"swi:length"}->{"swi:source"}->{$statType};
    my $newDup =
      $objNew->{"swi:statistic"}->{"swi:duplication"}->{"swi:symbols"}
      ->{$statType};

    if ( $objBase->{"swi:statistic"}->{"swi:checksum"}->{"swi:source"}
        ->{$statType}->{'content'} != $newCrc
        || $objBase->{"swi:statistic"}->{"swi:length"}->{"swi:source"}
        ->{$statType}->{'content'} != $newLength )
    {
        return "modified";
    }
    if ( $objBase->{"swi:statistic"}->{"swi:duplication"}->{"swi:symbols"}
        ->{$statType}->{'content'} != $newDup )
    {
        return "cloned";
    }

    return "unmodified";
}

sub swiCheckUselessPatterns
{
    my $root = shift();
    if ( ref($root) eq "HASH" )
    {
        foreach my $key ( keys %{$root} )
        {
            if ( $key eq 'swi:pattern' )
            {
                foreach my $pattern ( @{ $root->{'swi:pattern'} } )
                {
                    if ( !defined( $pattern->{'swi:used'} )
                        || $pattern->{'swi:used'} == 0 )
                    {
                        my $data = Dumper($pattern);
                        $data =~ s/\n/ /g;
                        $data =~ s/\s+/ /g;
                        STATUS(
"Useless suppress option detected with the following content: $data"
                        );
                    }
                }

                return;
            }
            swiCheckUselessPatterns( $root->{$key} );
        }
    }
    elsif ( ref($root) eq "ARRAY" )
    {
        foreach ( @{$root} )
        {
            return swiCheckUselessPatterns($_);
        }
    }

    return;
}

return 1;
