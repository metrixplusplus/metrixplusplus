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

#
# Export section
#
require Exporter;
use vars qw($VERSION @ISA @EXPORT @EXPORT_OK $PREFERRED_PARSER);
@ISA              = qw(Exporter);
@EXPORT           = qw(swiLaunch);
@EXPORT_OK        = qw();
$VERSION          = '1.0';
$PREFERRED_PARSER = undef;

#
# Subroutine for troubleshooting purposes
#
use Internal::Output;

#
# Include SWI libs
#
require SWI::Appraiser;
require SWI::Converter;
require SWI::Merger;
require SWI::Processor;

#
# Global variables
#
my $config = undef;

#
# Enter point
#
sub swiLaunch
{
    my $returnCode       = 0;
    my $rootLocation     = shift();
    my $swiConfiguration = shift();

    # $returnCode == 0 => no critical errors and warnings
    # $returnCode >  0 => no critical errors, there are warnings
    # $returnCode <  0 => there are critical errors

    if ( $returnCode >= 0 )
    {
        if ( $swiConfiguration eq "" )
        {
            STATUS("Configuration file should be specified!");
            $returnCode = -1;
        }
        else
        {
            STATUS("Configuration file: $swiConfiguration.");
        }
    }

    if ( $returnCode >= 0 )
    {
        if ( swiConfigurationValidate($swiConfiguration) != 0 )
        {
            STATUS("Wrong configuration file!");
            $returnCode = -2;
        }
    }

    if ( $returnCode >= 0 )
    {

        # Generate report for every module separately
        for (
            my $i = 0 ;
            $i <= $#{ $config->{"swi:modules"}->{"swi:module"} } ;
            $i++
          )
        {
            STATUS( "Processing module: '"
                  . $config->{"swi:modules"}->{"swi:module"}[$i]->{"swi:name"}
                  . "'." );
            my $result = swiProcess( $config, $i, $rootLocation );
            if ( $result < 0 )
            {
                STATUS("The are problems to report the index for the module!");
                $returnCode = -5;
            }
            elsif ( $result > 0 )
            {
                STATUS("The are scan warnings and/or errors.");
                $returnCode = $result;
            }
            else
            {
                STATUS("The module has been processed succesfully.");
            }
        }
    }

    if ( $returnCode >= 0 )
    {

        # Merge reports
        if ( swiMerge($config) )
        {
            STATUS("The are problems to merge files to one report!");
            $returnCode = -3;
        }
        else
        {
            STATUS("Merged report has been created.");
        }
    }

    if ( $returnCode >= 0 )
    {

        # Add average/min/max/total values and generate final XML report
        if ( swiAppraise($config) )
        {
            STATUS("The are problems to add average/min/max/total values!");
            $returnCode = -4;
        }
        else
        {
            STATUS("Average/min/max/total values have been added.");
        }
    }

    if ( $returnCode >= 0 )
    {

        # Convert results
        my $result = swiConvert($config);
        if ( $result < 0 )
        {
            STATUS("The are problems to convert the report!");
            $returnCode = -5;
        }
        elsif ( $result > 0 )
        {
            STATUS(
                "Report has been converted. There are exceeded limitations.");
            $returnCode = $result;
        }
        else
        {
            STATUS("Report has been converted.");
        }
    }

    return $returnCode;
}

sub swiConfigurationValidate
{
    my $result = 0;
    $config =
      XMLin( shift(),
        ForceArray => [ "swi:module", "swi:rule", "swi:pattern" ] );

    if ( !defined( $config->{'swi:info'} ) )
    {
        STATUS("Wrong configuration: 'swi:info' section missed.");
        $result++;
    }
    else
    {
        if ( !defined( $config->{'swi:info'}->{'swi:version'} ) )
        {
            STATUS(
                "Wrong configuration: 'swi:info/swi:version' section missed.");
            $result++;
        }
        elsif ( $config->{'swi:info'}->{'swi:version'} != 1 )
        {
            STATUS(
"Wrong configuration: Unsupported version of the configuration file. Check 'swi:info/swi:version' section."
            );
            $result++;
        }

        if ( !defined( $config->{'swi:info'}->{'swi:project'} ) )
        {
            STATUS(
                "Wrong configuration: 'swi:info/swi:project' section missed.");
            $result++;
        }
        else
        {
            if (
                !defined(
                    $config->{'swi:info'}->{'swi:project'}->{'swi:name'}
                )
              )
            {
                STATUS(
"Wrong configuration: 'swi:info/swi:project/swi:name' section missed."
                );
                $result++;
            }
            elsif ( $config->{'swi:info'}->{'swi:project'}->{'swi:name'} eq "" )
            {
                STATUS(
"Wrong configuration: 'swi:info/swi:project/swi:name' is empty."
                );
                $result++;
            }
        }
    }

    if ( !defined( $config->{'swi:general'} )
        || ref( $config->{'swi:general'} ) ne 'HASH' )
    {
        $config->{'swi:general'} = {};
    }
    if ( !defined( $config->{'swi:general'}->{'swi:debug'} )
        || ref( $config->{'swi:general'}->{'swi:debug'} ) ne 'HASH' )
    {
        $config->{'swi:general'}->{'swi:debug'} = {};
    }
    if ( !defined( $config->{'swi:general'}->{'swi:debug'}->{'swi:enabled'} ) )
    {
        $config->{'swi:general'}->{'swi:debug'}->{'swi:enabled'} = 'off';
    }
    DEBUG_ENABLED(
        ( $config->{'swi:general'}->{'swi:debug'}->{'swi:enabled'} eq 'on' )
        ? 1
        : 0
    );

    if ( !defined( $config->{'swi:modules'} )
        || ref( $config->{'swi:modules'} ) ne 'HASH' )
    {
        STATUS("Wrong configuration: 'swi:modules' section missed.");
        $result++;
    }
    else
    {
        if ( !defined( $config->{'swi:modules'}->{'swi:module'} )
            || ref( $config->{'swi:modules'}->{'swi:module'} ) ne 'ARRAY' )
        {
            STATUS(
                "Wrong configuration: 'swi:modules/swi:module' section missed."
            );
            $result++;
        }
        else
        {
            my $moduleId = 0;
            foreach my $module ( @{ $config->{'swi:modules'}->{'swi:module'} } )
            {
                if ( !defined( $module->{'swi:name'} ) )
                {
                    STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:name' section missed."
                    );
                    $result++;
                }
                if ( !defined( $module->{'swi:location'} ) )
                {
                    STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:location' section missed."
                    );
                    $result++;
                }

                if ( !defined( $module->{'swi:files'} )
                    || ref( $module->{'swi:files'} ) ne 'HASH' )
                {
                    $module->{'swi:files'} = {};
                }
                if ( !defined( $module->{'swi:files'}->{'swi:include'} ) )
                {
                    $module->{'swi:files'}->{'swi:include'} = '.*';
                }
                if ( !defined( $module->{'swi:files'}->{'swi:exclude'} ) )
                {
                    $module->{'swi:files'}->{'swi:exclude'} = '';
                }

                if ( !defined( $module->{'swi:preprocessor'} )
                    || ref( $module->{'swi:preprocessor'} ) ne 'HASH' )
                {
                    $module->{'swi:preprocessor'} = {};
                }
                if ( !defined( $module->{'swi:preprocessor'}->{'swi:rule'} ) )
                {
                    $module->{'swi:preprocessor'}->{'swi:rule'} = [];
                }

                my $ruleId = 0;
                foreach
                  my $rule ( @{ $module->{'swi:preprocessor'}->{'swi:rule'} } )
                {
                    if ( !defined( $rule->{'swi:filepattern'} )
                        || $rule->{'swi:filepattern'} eq "" )
                    {
                        STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:preprocessor/swi:rule[$ruleId]/swi:filepattern' section missed."
                        );
                        $result++;
                    }
                    if ( !defined( $rule->{'swi:searchpattern'} )
                        || $rule->{'swi:searchpattern'} eq "" )
                    {
                        STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:preprocessor/swi:rule[$ruleId]/swi:searchpattern' section missed."
                        );
                        $result++;
                    }
                    if ( !defined( $rule->{'swi:replacepattern'} )
                        || $rule->{'swi:replacepattern'} eq "" )
                    {
                        STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:preprocessor/swi:rule[$ruleId]/swi:replacepattern' section missed."
                        );
                        $result++;
                    }

                    $ruleId++;
                }

                if ( !defined( $module->{'swi:scanner'} )
                    || ref( $module->{'swi:scanner'} ) ne 'HASH' )
                {
                    $module->{'swi:scanner'} = {};
                }
                if ( !defined( $module->{'swi:scanner'}->{'swi:rule'} ) )
                {
                    $module->{'swi:scanner'}->{'swi:rule'} = [];
                }

                $ruleId = 0;
                foreach my $rule ( @{ $module->{'swi:scanner'}->{'swi:rule'} } )
                {
                    if ( !defined( $rule->{'swi:filepattern'} )
                        || $rule->{'swi:filepattern'} eq "" )
                    {
                        STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:scanner/swi:rule[$ruleId]/swi:filepattern' section missed."
                        );
                        $result++;
                    }
                    if ( !defined( $rule->{'swi:searchpattern'} )
                        || $rule->{'swi:searchpattern'} eq "" )
                    {
                        STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:scanner/swi:rule[$ruleId]/swi:searchpattern' section missed."
                        );
                        $result++;
                    }
                    if ( !defined( $rule->{'swi:messagepattern'} )
                        || $rule->{'swi:messagepattern'} eq "" )
                    {
                        STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:scanner/swi:rule[$ruleId]/swi:messagepattern' section missed."
                        );
                        $result++;
                    }

                    if ( !defined( $rule->{'swi:codecontent'} )
                        || $rule->{'swi:codecontent'} eq "" )
                    {
                        $rule->{'swi:codecontent'} = 'purified';
                    }

                    $ruleId++;
                }

                if ( !defined( $module->{'swi:scanner'}->{'swi:suppress'} ) )
                {
                    $module->{'swi:scanner'}->{'swi:suppress'} = {};
                }
                if (
                    !defined(
                        $module->{'swi:scanner'}->{'swi:suppress'}
                          ->{'swi:pattern'}
                    )
                  )
                {
                    $module->{'swi:scanner'}->{'swi:suppress'}
                      ->{'swi:pattern'} = [];
                }

                my $patternId = 0;
                foreach my $pattern (
                    @{
                        $module->{'swi:scanner'}->{'swi:suppress'}
                          ->{'swi:pattern'}
                    }
                  )
                {
                    if ( ref($pattern) ne 'HASH' )
                    {
                        STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:scanner/swi:suppress/swi:pattern[$patternId]' section is incorrect."
                        );
                        $result++;
                    }
                    else
                    {
                        if ( !defined( $pattern->{'swi:message'} )
                            || $pattern->{'swi:message'} eq "" )
                        {
                            STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:scanner/swi:suppress/swi:pattern[$patternId]/swi:message' field is empty."
                            );
                            $result++;
                        }
                        if ( !defined( $pattern->{'content'} )
                            || $pattern->{'content'} eq "" )
                        {
                            STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:scanner/swi:suppress/swi:pattern[$patternId]' object pattern is empty."
                            );
                            $result++;
                        }
                    }

                    $patternId++;
                }

                if ( !defined( $module->{'swi:indexer:common'} )
                    || ref( $module->{'swi:indexer:common'} ) ne 'HASH' )
                {
                    $module->{'swi:indexer:common'} = {};
                }

                if ( !defined( $module->{'swi:indexer:dup'} )
                    || ref( $module->{'swi:indexer:dup'} ) ne 'HASH' )
                {
                    $module->{'swi:indexer:dup'} = {};
                }
                if (
                    !defined(
                        $module->{'swi:indexer:dup'}->{'swi:codecontent'}
                    )
                  )
                {
                    $module->{'swi:indexer:dup'}->{'swi:codecontent'} =
                      'purified';
                }
                if ( !defined( $module->{'swi:indexer:dup'}->{'swi:enabled'} ) )
                {
                    $module->{'swi:indexer:dup'}->{'swi:enabled'} = 'off';
                }
                if ( !defined( $module->{'swi:indexer:dup'}->{'swi:minlength'} )
                  )
                {
                    $module->{'swi:indexer:dup'}->{'swi:minlength'} = 100;
                }
                if ( $module->{'swi:indexer:dup'}->{'swi:minlength'} <= 0 )
                {
                    STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:indexer:dup/swi:minlength' can not be less than or equal to zero."
                    );
                    $result++;
                }
                if ( !defined( $module->{'swi:indexer:dup'}->{'swi:proximity'} )
                  )
                {
                    $module->{'swi:indexer:dup'}->{'swi:proximity'} = 100;
                }
                if (   $module->{'swi:indexer:dup'}->{'swi:proximity'} <= 0
                    || $module->{'swi:indexer:dup'}->{'swi:proximity'} > 100 )
                {
                    STATUS(
"Wrong configuration: 'swi:modules/swi:module[$moduleId]/swi:indexer:dup/swi:proximity' should be in the range from 1 till 100."
                    );
                    $result++;
                }
                if (
                    !defined(
                        $module->{'swi:indexer:dup'}->{'swi:globalcode'}
                    )
                  )
                {
                    $module->{'swi:indexer:dup'}->{'swi:globalcode'} = 'off';
                }

                if ( !defined( $module->{'swi:indexer:gcov'} )
                    || ref( $module->{'swi:indexer:gcov'} ) ne 'HASH' )
                {
                    $module->{'swi:indexer:gcov'} = {};
                }
                if ( !defined( $module->{'swi:indexer:gcov'}->{'swi:enabled'} ) )
                {
                    $module->{'swi:indexer:gcov'}->{'swi:enabled'} = 'off';
                }
                if ( !defined( $module->{'swi:indexer:gcov'}->{'swi:filepattern'} ) )
                {
                    $module->{'swi:indexer:gcov'}->{'swi:filepattern'} = '.*';
                }
                if ( !defined( $module->{'swi:indexer:gcov'}->{'swi:sourcefile'} ) )
                {
                    $module->{'swi:indexer:gcov'}->{'swi:sourcefile'} = '(.*)[.][cChH][pP]?[pP]?';
                }
                if ( !defined( $module->{'swi:indexer:gcov'}->{'swi:gcdafile'} ) )
                {
                    $module->{'swi:indexer:gcov'}->{'swi:gcdafile'} = '${1}.gcda';
                }

                $moduleId++;
            }
        }
    }

    if ( !defined( $config->{'swi:report'} )
        || ref( $config->{'swi:report'} ) ne 'HASH' )
    {
        STATUS("Wrong configuration: 'swi:report' section missed.");
        $result++;
    }
    else
    {
        if ( !defined( $config->{'swi:report'}->{'swi:destination'} ) )
        {
            STATUS(
"Wrong configuration: 'swi:report/swi:destination' section missed."
            );
            $result++;
        }

        if ( !defined( $config->{'swi:report'}->{'swi:xml'} ) )
        {
            STATUS("Wrong configuration: 'swi:report/swi:xml' section missed.");
            $result++;
        }
        else
        {
            if (
                !defined( $config->{'swi:report'}->{'swi:xml'}->{'swi:name'} ) )
            {
                STATUS(
"Wrong configuration: 'swi:report/swi:xml/swi:name' section is empty."
                );
                $result++;
            }
        }

        if ( !defined( $config->{'swi:report'}->{'swi:notifications'} ) )
        {
            STATUS(
"Wrong configuration: 'swi:report/swi:notifications' section missed."
            );
            $result++;
        }
        else
        {
            if (
                !defined(
                    $config->{'swi:report'}->{'swi:notifications'}->{'swi:name'}
                )
              )
            {
                STATUS(
"Wrong configuration: 'swi:report/swi:notifications/swi:name' section is empty."
                );
                $result++;
            }

            if (
                !defined(
                    $config->{'swi:report'}->{'swi:notifications'}
                      ->{'swi:error'}
                )
                || ref(
                    $config->{'swi:report'}->{'swi:notifications'}
                      ->{'swi:error'}
                ) ne 'HASH'
              )
            {
                $config->{'swi:report'}->{'swi:notifications'}->{'swi:error'} =
                  {};
            }
            if (
                !defined(
                    $config->{'swi:report'}->{'swi:notifications'}
                      ->{'swi:error'}->{'swi:added'}
                )
              )
            {
                $config->{'swi:report'}->{'swi:notifications'}->{'swi:error'}
                  ->{'swi:added'} = 'on';
            }
            if (
                !defined(
                    $config->{'swi:report'}->{'swi:notifications'}
                      ->{'swi:error'}->{'swi:removed'}
                )
              )
            {
                $config->{'swi:report'}->{'swi:notifications'}->{'swi:error'}
                  ->{'swi:removed'} = 'on';
            }
            if (
                !defined(
                    $config->{'swi:report'}->{'swi:notifications'}
                      ->{'swi:error'}->{'swi:modified'}
                )
              )
            {
                $config->{'swi:report'}->{'swi:notifications'}->{'swi:error'}
                  ->{'swi:modified'} = 'on';
            }
            if (
                !defined(
                    $config->{'swi:report'}->{'swi:notifications'}
                      ->{'swi:error'}->{'swi:cloned'}
                )
              )
            {
                $config->{'swi:report'}->{'swi:notifications'}->{'swi:error'}
                  ->{'swi:cloned'} = 'on';
            }
            if (
                !defined(
                    $config->{'swi:report'}->{'swi:notifications'}
                      ->{'swi:error'}->{'swi:unmodified'}
                )
              )
            {
                $config->{'swi:report'}->{'swi:notifications'}->{'swi:error'}
                  ->{'swi:unmodified'} = 'on';
            }

            if (
                !defined(
                    $config->{'swi:report'}->{'swi:notifications'}
                      ->{'swi:print'}
                )
                || ref(
                    $config->{'swi:report'}->{'swi:notifications'}
                      ->{'swi:print'}
                ) ne 'HASH'
              )
            {
                $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'} =
                  {};
            }
            swiUtilConfigFill_PrintSection($config, 'swi:added');
            swiUtilConfigFill_PrintSection($config, 'swi:removed');
            swiUtilConfigFill_PrintSection($config, 'swi:modified');
            swiUtilConfigFill_PrintSection($config, 'swi:cloned');
            swiUtilConfigFill_PrintSection($config, 'swi:unmodified');
            
        }
    }
    
    # swi:limits section is verified in runtime
    # no precheck currently 

    DEBUG( "Configuration structure is: " . Dumper($config) );
    return $result;
}

sub swiUtilConfigFill_PrintSection
{
    my $config  = shift();
    my $modType = shift();

    if (
        !defined(
            $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
              ->{$modType}
        )
        || ref(
            $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
              ->{$modType}
        ) ne 'HASH'
      )
    {
        $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
          ->{$modType} = {};
    }
    
    if (
        !defined(
            $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
              ->{$modType}->{'swi:failures'}
        )
      )
    {
        $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
          ->{$modType}->{'swi:failures'} = 'on';
    }
    if (
        !defined(
            $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
              ->{$modType}->{'swi:modifications'}
        )
      )
    {
        $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
          ->{$modType}->{'swi:modifications'} = 'on';
    }
    if (
        !defined(
            $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
              ->{$modType}->{'swi:duplications'}
        )
      )
    {
        $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
          ->{$modType}->{'swi:duplications'} = 'on';
    }
    if (
        !defined(
            $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
              ->{$modType}->{'swi:scanmessages'}
        )
      )
    {
        $config->{'swi:report'}->{'swi:notifications'}->{'swi:print'}
          ->{$modType}->{'swi:scanmessages'} = 'on';
    }
}

return 1;
