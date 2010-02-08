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
                  . $config->{"swi:modules"}->{"swi:module"}[$i]
                  ->{"swi:name"} . "'." );
            my $result = swiProcess( $config, $i, $rootLocation );
            if ( $result < 0 )
            {
                STATUS(
                    "The are problems to report the index for the module!");
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
            STATUS(
                "The are problems to add average/min/max/total values!");
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
            STATUS("Report has been converted. There are exceeded limitations.");
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
    $config =
      XMLin( shift(),
        ForceArray => [ "swi:module", "swi:rule", "swi:pattern" ] );

    DEBUG("Configuration structure is: " . Dumper($config));
    return 0;
}

return 1;
