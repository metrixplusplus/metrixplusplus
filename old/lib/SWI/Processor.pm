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
use Data::Dumper;
use FileHandle;
use IPC::Open3;

use XML::Simple;
use String::CRC::Cksum;

#
# Export section
#
require Exporter;
use vars qw($VERSION @ISA @EXPORT @EXPORT_OK $PREFERRED_PARSER);
@ISA              = qw(Exporter);
@EXPORT           = qw(swiProcess);
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
my @crctab = (
    0x00000000, 0x04c11db7, 0x09823b6e, 0x0d4326d9, 0x130476dc, 0x17c56b6b,
    0x1a864db2, 0x1e475005, 0x2608edb8, 0x22c9f00f, 0x2f8ad6d6, 0x2b4bcb61,
    0x350c9b64, 0x31cd86d3, 0x3c8ea00a, 0x384fbdbd, 0x4c11db70, 0x48d0c6c7,
    0x4593e01e, 0x4152fda9, 0x5f15adac, 0x5bd4b01b, 0x569796c2, 0x52568b75,
    0x6a1936c8, 0x6ed82b7f, 0x639b0da6, 0x675a1011, 0x791d4014, 0x7ddc5da3,
    0x709f7b7a, 0x745e66cd, 0x9823b6e0, 0x9ce2ab57, 0x91a18d8e, 0x95609039,
    0x8b27c03c, 0x8fe6dd8b, 0x82a5fb52, 0x8664e6e5, 0xbe2b5b58, 0xbaea46ef,
    0xb7a96036, 0xb3687d81, 0xad2f2d84, 0xa9ee3033, 0xa4ad16ea, 0xa06c0b5d,
    0xd4326d90, 0xd0f37027, 0xddb056fe, 0xd9714b49, 0xc7361b4c, 0xc3f706fb,
    0xceb42022, 0xca753d95, 0xf23a8028, 0xf6fb9d9f, 0xfbb8bb46, 0xff79a6f1,
    0xe13ef6f4, 0xe5ffeb43, 0xe8bccd9a, 0xec7dd02d, 0x34867077, 0x30476dc0,
    0x3d044b19, 0x39c556ae, 0x278206ab, 0x23431b1c, 0x2e003dc5, 0x2ac12072,
    0x128e9dcf, 0x164f8078, 0x1b0ca6a1, 0x1fcdbb16, 0x018aeb13, 0x054bf6a4,
    0x0808d07d, 0x0cc9cdca, 0x7897ab07, 0x7c56b6b0, 0x71159069, 0x75d48dde,
    0x6b93dddb, 0x6f52c06c, 0x6211e6b5, 0x66d0fb02, 0x5e9f46bf, 0x5a5e5b08,
    0x571d7dd1, 0x53dc6066, 0x4d9b3063, 0x495a2dd4, 0x44190b0d, 0x40d816ba,
    0xaca5c697, 0xa864db20, 0xa527fdf9, 0xa1e6e04e, 0xbfa1b04b, 0xbb60adfc,
    0xb6238b25, 0xb2e29692, 0x8aad2b2f, 0x8e6c3698, 0x832f1041, 0x87ee0df6,
    0x99a95df3, 0x9d684044, 0x902b669d, 0x94ea7b2a, 0xe0b41de7, 0xe4750050,
    0xe9362689, 0xedf73b3e, 0xf3b06b3b, 0xf771768c, 0xfa325055, 0xfef34de2,
    0xc6bcf05f, 0xc27dede8, 0xcf3ecb31, 0xcbffd686, 0xd5b88683, 0xd1799b34,
    0xdc3abded, 0xd8fba05a, 0x690ce0ee, 0x6dcdfd59, 0x608edb80, 0x644fc637,
    0x7a089632, 0x7ec98b85, 0x738aad5c, 0x774bb0eb, 0x4f040d56, 0x4bc510e1,
    0x46863638, 0x42472b8f, 0x5c007b8a, 0x58c1663d, 0x558240e4, 0x51435d53,
    0x251d3b9e, 0x21dc2629, 0x2c9f00f0, 0x285e1d47, 0x36194d42, 0x32d850f5,
    0x3f9b762c, 0x3b5a6b9b, 0x0315d626, 0x07d4cb91, 0x0a97ed48, 0x0e56f0ff,
    0x1011a0fa, 0x14d0bd4d, 0x19939b94, 0x1d528623, 0xf12f560e, 0xf5ee4bb9,
    0xf8ad6d60, 0xfc6c70d7, 0xe22b20d2, 0xe6ea3d65, 0xeba91bbc, 0xef68060b,
    0xd727bbb6, 0xd3e6a601, 0xdea580d8, 0xda649d6f, 0xc423cd6a, 0xc0e2d0dd,
    0xcda1f604, 0xc960ebb3, 0xbd3e8d7e, 0xb9ff90c9, 0xb4bcb610, 0xb07daba7,
    0xae3afba2, 0xaafbe615, 0xa7b8c0cc, 0xa379dd7b, 0x9b3660c6, 0x9ff77d71,
    0x92b45ba8, 0x9675461f, 0x8832161a, 0x8cf30bad, 0x81b02d74, 0x857130c3,
    0x5d8a9099, 0x594b8d2e, 0x5408abf7, 0x50c9b640, 0x4e8ee645, 0x4a4ffbf2,
    0x470cdd2b, 0x43cdc09c, 0x7b827d21, 0x7f436096, 0x7200464f, 0x76c15bf8,
    0x68860bfd, 0x6c47164a, 0x61043093, 0x65c52d24, 0x119b4be9, 0x155a565e,
    0x18197087, 0x1cd86d30, 0x029f3d35, 0x065e2082, 0x0b1d065b, 0x0fdc1bec,
    0x3793a651, 0x3352bbe6, 0x3e119d3f, 0x3ad08088, 0x2497d08d, 0x2056cd3a,
    0x2d15ebe3, 0x29d4f654, 0xc5a92679, 0xc1683bce, 0xcc2b1d17, 0xc8ea00a0,
    0xd6ad50a5, 0xd26c4d12, 0xdf2f6bcb, 0xdbee767c, 0xe3a1cbc1, 0xe760d676,
    0xea23f0af, 0xeee2ed18, 0xf0a5bd1d, 0xf464a0aa, 0xf9278673, 0xfde69bc4,
    0x89b8fd09, 0x8d79e0be, 0x803ac667, 0x84fbdbd0, 0x9abc8bd5, 0x9e7d9662,
    0x933eb0bb, 0x97ffad0c, 0xafb010b1, 0xab710d06, 0xa6322bdf, 0xa2f33668,
    0xbcb4666d, 0xb8757bda, 0xb5365d03, 0xb1f740b4
);

#
# Brackets/hooks '()' in regexp are not acceptable in declarations below
# TODO: configure individually for every language
#
my $regexpCommentSingle     = '//';
my $regexpCommentMultiStart = '/\\*';
my $regexpCommentMultiEnd   = '\\*/';
my $regexpCodeBlockStart    = '{';
my $regexpCodeBlockEnd      = '}';
my $regexpCodeKeyword       = 'case|do|else|if|for|switch|while';
my $regexpCodeStatements    =
'\s*[^;]*[;]\s*|\s*extern\s+["]{2}\s*|\s*protected\s*[:]\s*|\s*private\s*[:]\s*|\s*public\s*[:]\s*';
my $regexpCodeFunctionIdentifier =
'([_a-zA-Z~][_a-zA-Z0-9~]*\s*[:][:]\s*)*((operator[^a-zA-Z0-9_][^(]*)|([_a-zA-Z~][_a-zA-Z0-9]*))';
my $regexpCodeFunctionModifier    = '[_a-zA-Z0-9:*&><, \t\n]*\s+[*&]?[*&]?\s*';
my $regexpCodeFunctionArguments   = '\s*\([^;]+\s*';
my $regexpCodeContainerIdentifier = '[_a-zA-Z][_a-zA-Z0-9]*';
my $regexpCodeContainerModifier   =
'\s*class|\s*template\s*<[^;]+>\s*class|\s*namespace|\s*template\s*<[^;]+>\s*struct|\s*struct|\s*static\s+struct|\s*static\s+union|\s*static\s+class|\s*enum|\s*typedef|\s*typedef\s+struct|\s*typedef\s+enum|\s*union|\s*typedef\s+union';
my $regexpCodeContainerArguments = '\s*[^;]*\s*';
my $regexpCodeContainerDelimeter = '::';
my $regexpCodeBlockStartIgnore   =
  '=\s*|,\s*|\s*enum\s*|\s*union\s*|\s*struct\s*';
my $regexpCodeStringBorder_Escape =
  '(([^\\\](\\\\\\\\)*\\\\)|^([\\\](\\\\\\\\)*))';
my $regexpCodeStringBorder_Text          = '["\']';
my $regexpCodePreprocessorStart          = '^[ \t]*#';
my $regexpCodePreprocessorEnd            = '[^\\\\]\s*$';
my $regexpCodeMatch_ComplexityCyclomatic =
  '([^0-9A-Za-z_]((if)|(case)|(for)|(while))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]"';
my $regexpCodeGlobalFunctionName = '>>>GLOBAL<<<';

#
# Handler for dupindex tool
#
my $dupindexHandler = undef;
my $dupindexIn      = undef;
my $dupindexOut     = undef;
my $dupindexErr     = undef;

#
# Errors counter, this global variable incremented if some inconsistency detected
#
my $exitCode = 0;

#
# Enter point
#
sub swiProcess
{
    my $returnCode = 0;

    my $config       = shift();
    my $moduleId     = shift();
    my $rootLocation = shift();

    my $swiGlobalDirectory =
      $config->{"swi:modules"}->{"swi:module"}[$moduleId]->{"swi:location"};
    my $swiGlobalReportLocation =
        $config->{"swi:report"}->{"swi:destination"} . "/"
      . $config->{"swi:report"}->{"swi:xml"}->{"swi:name"}
      . ".$moduleId";
    my $swiGlobalModuleName =
      $config->{"swi:modules"}->{"swi:module"}[$moduleId]->{"swi:name"};
    my $swiGlobalInclude =
      $config->{"swi:modules"}->{"swi:module"}[$moduleId]->{"swi:files"}
      ->{"swi:include"};
    my $swiGlobalExclude =
      $config->{"swi:modules"}->{"swi:module"}[$moduleId]->{"swi:files"}
      ->{"swi:exclude"};
    my $swiGlobalReportName =
      $config->{"swi:info"}->{"swi:project"}->{"swi:name"};
    my $swiGlobalPreprocessorRules =
      $config->{"swi:modules"}->{"swi:module"}[$moduleId]->{"swi:preprocessor"}
      ->{"swi:rule"};
    my $swiGlobalScanerRules =
      $config->{"swi:modules"}->{"swi:module"}[$moduleId]->{"swi:scanner"}
      ->{"swi:rule"};
    my $swiGlobalDupfinderEnabled =
      $config->{"swi:modules"}->{"swi:module"}[$moduleId]->{"swi:indexer:dup"}
      ->{"swi:enabled"};

    if ( $returnCode == 0 )
    {
        if ( $swiGlobalDirectory eq "" )
        {
            STATUS(
                "Wrong configuration: source directory should be specified!");
            $returnCode = -1;
        }
    }

    if ( $returnCode == 0 )
    {
        if ( $swiGlobalReportLocation eq "" )
        {
            STATUS(
                "Wrong configuiration: report location should be specified!");
            $returnCode = -2;
        }
    }

    if ( not defined($swiGlobalInclude) )
    {
        $swiGlobalInclude = '.*';
    }

    if ( $returnCode == 0 )
    {
        my $filesData = {};

        $dupindexHandler =
          open3( $dupindexIn, $dupindexOut, $dupindexErr,
            "$rootLocation/dupindex/bin/dupindex.exe" );
        if (   !defined($dupindexHandler)
            || !defined($dupindexIn)
            || !defined($dupindexOut) )
        {
            die(
"Can not start the internal platform native tool '$rootLocation/dupindex/bin/dupindex.exe'"
            );
        }

        my $dupfinderSettings =
          $config->{"swi:modules"}->{"swi:module"}[$moduleId]
          ->{"swi:indexer:dup"};
        if ( defined( $dupfinderSettings->{"swi:minlength"} ) )
        {
            print $dupindexIn "init_length\n";
            print $dupindexIn $dupfinderSettings->{"swi:minlength"} . "\n";
        }
        if ( defined( $dupfinderSettings->{"swi:proximity"} ) )
        {
            print $dupindexIn "init_proximity\n";
            print $dupindexIn $dupfinderSettings->{"swi:proximity"} . "\n";
        }

        # TODO: configure individually for every language
        # see for todos in dupindex.cpp file
        #print $dupindexIn "init_ignorable\n";
        #print $dupindexIn "\n";
        #print $dupindexIn "init_nonregular\n";
        #print $dupindexIn "\n";
        
        my @directories;
        push(@directories, $swiGlobalDirectory);

        foreach my $curDirectory (@directories)
        {
            opendir( DIR, $curDirectory )
                or die("Can not open source directory '$curDirectory'!");
            while ( my $file = readdir(DIR) )
            {
                my $fullPathFile = $curDirectory . "/" . $file;
                if ($file eq '.' || $file eq '..')
                {
                    next;
                }
                if (-d ($fullPathFile))
                {
                    push(@directories, $fullPathFile);
                    next;
                }
                
                $fullPathFile =~ s/$swiGlobalDirectory\///;
                if ( $fullPathFile =~ m/$swiGlobalInclude/ )
                {
                    if (   $swiGlobalExclude ne ""
                        && $fullPathFile =~ m/$swiGlobalExclude/ )
                    {
                        next;
                    }
                    
                    $filesData->{$fullPathFile} = swiParse(
                        $swiGlobalDirectory,
                        $fullPathFile,
                        $swiGlobalPreprocessorRules,
                        $swiGlobalScanerRules,
                        $config->{"swi:modules"}->{"swi:module"}[$moduleId]
                            ->{"swi:indexer:dup"},
                        $config->{"swi:modules"}->{"swi:module"}[$moduleId]
                            ->{"swi:indexer:gcov"}
                    );
                }
            }
            closedir(DIR);
        }

        # Add duplication statistics
        if ( defined($swiGlobalDupfinderEnabled)
            && $swiGlobalDupfinderEnabled eq 'on' )
        {
            $filesData = swiSourceIndexDuplicationAdd($filesData);
        }
        else
        {
            print $dupindexIn "exit\n";
        }

        # Prepare XML report
        STATUS("Generating the report '$swiGlobalReportLocation'...");

        swiXmlReportPrint(
            $filesData,               $swiGlobalDirectory,
            $swiGlobalReportLocation, $swiGlobalModuleName
        );

        $returnCode = $exitCode;
    }

    return $returnCode;
}

sub swiXmlReportPrint()
{
    my $filesData      = shift();
    my $curDir         = shift();
    my $reportLocation = shift();
    my $moduleName     = shift();

    $curDir =~ s/\n$//;

    my $fh = new FileHandle( "$reportLocation", "w" )
      or die("Can not open output file: $reportLocation!");

    print $fh "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n";
    print $fh "<swi:report>\n";
    print $fh "\n";

    print $fh "  <swi:module>\n";
    print $fh "    <swi:name>" . $moduleName . "</swi:name>\n";
    print $fh "    <swi:location>" . $curDir . "</swi:location>\n";
    print $fh "\n";

    print $fh "    <swi:info>\n";
    print $fh "      <swi:version>1</swi:version>\n";
    if ( defined( $ENV{USER} ) )
    {
        print $fh "      <swi:user>" . $ENV{USER} . "</swi:user>\n";
    }
    print $fh "      <swi:generator>SWI/PROCESSOR</swi:generator>\n";
    print $fh "    </swi:info>\n";
    print $fh "\n";

    my $filesCount     = 0;
    my $functionsCount = 0;
    foreach my $file ( keys %{$filesData} )
    {
        $filesCount++;

        print $fh "    <swi:file>\n";
        print $fh "      <swi:name>" . $file . "</swi:name>\n";
        print $fh "      <swi:location>" . $file . "</swi:location>\n";
        print $fh "\n";

        my $functions           = $filesData->{$file};
        my $localFunctionsCount = 0;
        foreach my $function ( keys %$functions )
        {
            $functionsCount++;
            $localFunctionsCount++;

            print $fh "      <swi:function>\n";
            print $fh "        " . XMLout( $function, RootName => 'swi:name' );
            print $fh "        "
              . XMLout(
                $file . ":"
                  . ( $functions->{$function}->{'swi:line:headerstart'} + 1 ),
                RootName => 'swi:location'
              );
            print $fh "        "
              . XMLout( $functions->{$function}->{'swi:modifier'},
                RootName => 'swi:modifier' );
            print $fh "        <swi:pointer"
              . " swi:headerstart=\""
              . ( $functions->{$function}->{'swi:line:headerstart'} + 1 ) . "\""
              . " swi:commentstart=\""
              . ( $functions->{$function}->{'swi:line:commentstart'} + 1 )
              . "\""
              . " swi:blockstart=\""
              . ( $functions->{$function}->{'swi:line:blockstart'} + 1 ) . "\""
              . " swi:blockend=\""
              . ( $functions->{$function}->{'swi:line:blockend'} + 1 ) . "\""
              . " />\n";

            my $statStr = XMLout(
                $functions->{$function}->{'swi:statistic'},
                RootName  => 'swi:statistic',
                GroupTags => {
                    'swi:complexity'  => '__REMOVE__',
                    'swi:duplication' => '__REMOVE__',
                    'swi:length'      => '__REMOVE__',
                    'swi:lines'       => '__REMOVE__',
                    'swi:checksum'    => '__REMOVE__',
                    'swi:coverage'    => '__REMOVE__'
                }
            );
            $statStr =~ s/\n/\n        /g;
            $statStr =~ s/ name="__REMOVE__"//g;
            print $fh "        ";
            print $fh $statStr;
            print $fh "\n";
            my $refStr = XMLout( $functions->{$function}->{'swi:reference'},
                RootName => '' );
            $refStr =~ s/\n/\n      /g;
            $refStr =~ s/<anon /<swi:reference /g;
            $refStr =~ s/<anon>\s*<\/anon>\s*/\n/g;
            print $fh "      ";
            print $fh $refStr;
            print $fh "      </swi:function>\n";
            print $fh "\n";
        }

        print $fh "      <swi:statistic>\n";
        print $fh "        <swi:count>\n";
        print $fh "          <swi:functions swi:exact=\""
          . $localFunctionsCount
          . "\" />\n";
        print $fh "        </swi:count>\n";
        print $fh "      </swi:statistic>\n";
        print $fh "\n";

        print $fh "    </swi:file>\n";
        print $fh "\n";
    }

    print $fh "    <swi:statistic>\n";
    print $fh "      <swi:count>\n";

# Warning: swi_merger requires to have counter of files before counters of functions
    print $fh "        <swi:files swi:exact=\"" . $filesCount . "\" />\n";
    print $fh "        <swi:functions swi:exact=\""
      . $functionsCount
      . "\" />\n";
    print $fh "      </swi:count>\n";
    print $fh "    </swi:statistic>\n";
    print $fh "\n";

    print $fh "  </swi:module>\n";
    print $fh "\n";
    print $fh "</swi:report>\n";

    $fh->close();
}

#
# Parser enter point
#
sub swiParse
{
    my $location          = shift();
    my $file              = shift();
    my $preprocessorRules = shift();
    my $scanerRules       = shift();
    my $dupfinderSettings = shift();
    my $gcovSettings      = shift();

    STATUS("Parsing file: '$location/$file'.");

    my $fh = new FileHandle( $location . "/" . $file, "r" )
      or die("Can not open input file '$location/$file'!");
    my @fileLines = <$fh>;

    # Get all types of strings
    my ( $globalBlock_Initial, $globalBlock_Code, $globalBlock_Comment ) =
      swiSourceCommentsDeattach(@fileLines);
    my $globalBlock_NoStr  = swiSourceCodeStringsRemove($globalBlock_Code);
    my $globalBlock_NoPrep = swiSourceCodePreprocessorRemove($globalBlock_Code);
    my $globalBlock_Purified = swiSourceCodeStringsRemove($globalBlock_NoPrep);

    # Preprocess purified code
    foreach my $rule ( @{$preprocessorRules} )
    {
        my $pattern = $rule->{'swi:filepattern'};
        if ( $file =~ m/$pattern/ )
        {
            $globalBlock_Purified = swiSourceCodePreprocess(
                $globalBlock_Purified,
                $rule->{'swi:searchpattern'},
                $rule->{'swi:replacepattern'}
            );
        }
    }

    # Parse source code
    my $functionsData =
      swiSourceCodeParse( $file, $globalBlock_Purified, $globalBlock_Comment );

    # Adjusting scaner rules (for performance purposes)
    my $scanerRulesFiltered = [];
    foreach my $rule ( @{$scanerRules} )
    {
        my $pattern = $rule->{'swi:filepattern'};
        if ( $file =~ m/$pattern/ )
        {
            push( @{$scanerRulesFiltered}, $rule );
        }
    }

    # Add statistics
    $functionsData = swiSourceIndexAdd(
        $file,                $functionsData,       $scanerRulesFiltered,
        $dupfinderSettings,   $globalBlock_Initial, $globalBlock_Code,
        $globalBlock_Comment, $globalBlock_NoPrep,  $globalBlock_NoStr,
        $globalBlock_Purified
    );

    if ( $gcovSettings->{'swi:enabled'} eq 'on' )
    {
        my $filePattern = $gcovSettings->{'swi:filepattern'};
        if ( $file =~ m/$filePattern/ )
        {
            swiSourceIndexGcovAdd(
                $location, $file, $functionsData,
                $gcovSettings->{'swi:sourcefile'},
                $gcovSettings->{'swi:gcdafile'}
            );
        }
    }

    return $functionsData;
}

sub swiSourceCodePreprocess
{
    my $code     = shift();
    my $search   = shift();
    my $replace  = shift();
    my $lastPart = $code;
    my $result   = "";

    my $posPrev    = 0;
    my $posCurrent = 0;

    while ( $code =~ m/$search/g )
    {

        $posPrev    = $posCurrent;
        $posCurrent = pos($code);

        my $matchStr = $&;
        $lastPart = $';

        my $replaceString = eval( 'my $tmp = "' . $replace . '";' );

        if ( swiMatchPatternCount( $matchStr, '\n' ) !=
            swiMatchPatternCount( $replaceString, '\n' ) )
        {
            die(
"Wrong preprocessor rule detected in the configuration file: it changes number of lines replacing the text\n>>>\n"
                  . $matchStr
                  . "\n<<<\nby\n>>>\n"
                  . $replaceString
                  . "\n<<<\n" );
        }

        my $blockFrag =
          substr( $code, $posPrev, $posCurrent - $posPrev - length($matchStr) );
        $result .= ( $blockFrag . $replaceString );
    }

    $result .= $lastPart;

    return $result;
}

sub swiSourceCodeScan
{
    my $file    = shift();
    my $offset  = shift();
    my $code    = shift();
    my $search  = shift();
    my $message = shift();
    my @result  = [];

    while ( $code =~ m/$search/g )
    {

        my $matchPre = $`;
        my $matchStr = $&;

        my $linePos = swiMatchPatternCount( $matchPre . $matchStr, '\n' ) + 1;
        my $messageString = eval( 'my $tmp = "' . $message . '";' );

        push(
            @result,
            {
                'swi:ref:type'     => 'scan',
                'swi:scan:file'    => $file,
                'swi:scan:line'    => $linePos + $offset,
                'swi:scan:message' => $messageString
            }
        );
    }

    return @result;
}

sub swiSourceCodeGlobalGet
{
    my $functionsData = shift();
    my $endLine       = shift();
    my @blockCodeAgr  = @_;
    my @blockCode;

    if ( $#blockCodeAgr == 0 )
    {

        # Continues code string provided
        @blockCode = split( "\n", $blockCodeAgr[0] );
    }
    else
    {

        # Array of lines provided
        @blockCode = @blockCodeAgr;
    }

    if ( !defined($endLine) )
    {
        # end line is the last by default
        $endLine = $#blockCode + 1;
    }

    foreach my $function ( values %{$functionsData} )
    {
        for (
            my $i = $function->{'swi:line:commentstart'} ;
            $i <= $function->{'swi:line:blockend'} ;
            $i++
          )
        {

            # Clear line if it is inside function
            $blockCode[$i] = "";
        }
    }

    my $result = "";
    my $emptyLines = "";
    foreach my $line (@blockCode)
    {
        # Check if it is necessary to finish
        $endLine--;
        if ( $endLine < 0 )
        {
            last;
        }
        
        # attach frag only if it is not empty
        if ($line =~ m/[^ \t]/)
        {
            $result .= $emptyLines . $line . "\n";
            $emptyLines = "";      
        }
        else
        {
            $emptyLines .= $line . "\n";
        }
    }

    return $result;
}

sub swiDupindexFunctionAdd
{
    my $fileName     = shift();
    my $functionName = shift();
    my $functionCode = shift();

    print $dupindexIn "init_file\n";
    print $dupindexIn length($fileName) . "\n";
    print $dupindexIn length($functionName) . "\n";
    print $dupindexIn length($functionCode) . "\n";
    print $dupindexIn $fileName . $functionName . $functionCode . "\n";
}

sub swiSourceIndexAdd
{
    my $file              = shift();
    my $functionsData     = shift();
    my $scanerRules       = shift();
    my $dupfinderSettings = shift();
    my @block_Initial     = split( "\n", shift() );
    my @block_Code        = split( "\n", shift() );
    my @block_Comment     = split( "\n", shift() );
    my @block_NoPrep      = split( "\n", shift() );
    my @block_NoStr       = split( "\n", shift() );
    my $block_Purified    = shift();

    # Extend arrays in order to remove warnings
    my $finalLinesNum = swiMatchPatternCount( $block_Purified, '\n' ) + 1;
    @block_Initial = swiUtilArrayExtend( [@block_Initial], $finalLinesNum, "" );
    @block_Code    = swiUtilArrayExtend( [@block_Code],    $finalLinesNum, "" );
    @block_Comment = swiUtilArrayExtend( [@block_Comment], $finalLinesNum, "" );
    @block_NoPrep  = swiUtilArrayExtend( [@block_NoPrep],  $finalLinesNum, "" );
    @block_NoStr   = swiUtilArrayExtend( [@block_NoStr],   $finalLinesNum, "" );

    foreach my $functionName ( keys %{$functionsData} )
    {
        my $function = $functionsData->{$functionName};

        my $block       = {};
        my $blockOffset = {};

        # Initialize function name
        $block->{'functionname'} = $functionName;
        $block->{'functionname'} =~
s/($regexpCodeContainerDelimeter)?($regexpCodeContainerIdentifier$regexpCodeContainerDelimeter)*($regexpCodeFunctionIdentifier)/$3/;
        $blockOffset->{'functionname'} = $function->{'swi:line:headerstart'};

        if ( $functionName ne $regexpCodeGlobalFunctionName )
        {

            # Get content
            $block->{'initial'}       = "";
            $blockOffset->{'initial'} = $function->{'swi:line:commentstart'};
            for (
                my $i = $function->{'swi:line:commentstart'} ;
                $i <= $function->{'swi:line:blockend'} ;
                $i++
              )
            {
                $block->{'initial'} .= $block_Initial[$i] . "\n";
            }
            $block->{'code'}       = "";
            $blockOffset->{'code'} = $function->{'swi:line:commentstart'};
            for (
                my $i = $function->{'swi:line:commentstart'} ;
                $i <= $function->{'swi:line:blockend'} ;
                $i++
              )
            {
                $block->{'code'} .= $block_Code[$i] . "\n";
            }
            $block->{'comments'}       = "";
            $blockOffset->{'comments'} = $function->{'swi:line:commentstart'};
            for (
                my $i = $function->{'swi:line:commentstart'} ;
                $i <= $function->{'swi:line:blockend'} ;
                $i++
              )
            {
                $block->{'comments'} .= $block_Comment[$i] . "\n";
            }
            $block->{'nopreprocessor'}       = "";
            $blockOffset->{'nopreprocessor'} =
              $function->{'swi:line:commentstart'};
            for (
                my $i = $function->{'swi:line:commentstart'} ;
                $i <= $function->{'swi:line:blockend'} ;
                $i++
              )
            {
                $block->{'nopreprocessor'} .= $block_NoPrep[$i] . "\n";
            }
            $block->{'nostrings'}       = "";
            $blockOffset->{'nostrings'} = $function->{'swi:line:commentstart'};
            for (
                my $i = $function->{'swi:line:commentstart'} ;
                $i <= $function->{'swi:line:blockend'} ;
                $i++
              )
            {
                $block->{'nostrings'} .= $block_NoStr[$i] . "\n";
            }
            $block->{'purified'} = substr(
                $block_Purified,
                $function->{'swi:pos:headerstart'},
                $function->{'swi:pos:blockend'} -
                  $function->{'swi:pos:headerstart'}
              )
              . "\n";
            $blockOffset->{'purified'} = $function->{'swi:line:headerstart'};
            $block->{'commentshead'}   = "";
            $blockOffset->{'commentshead'} =
              $function->{'swi:line:commentstart'};
            for (
                my $i = $function->{'swi:line:commentstart'} ;
                $i < $function->{'swi:line:headerstart'} ;
                $i++
              )
            {
                $block->{'commentshead'} .= $block_Comment[$i] . "\n";
            }

            $block->{'functionhead'} = substr(
                $block_Purified,
                $function->{'swi:pos:headerstart'},
                $function->{'swi:pos:blockstart'} -
                  $function->{'swi:pos:headerstart'}
              )
              . "\n";
            $blockOffset->{'functionhead'} =
              $function->{'swi:line:headerstart'};
            $block->{'functionbody'} = substr(
                $block_Purified,
                $function->{'swi:pos:blockstart'},
                $function->{'swi:pos:blockend'} -
                  $function->{'swi:pos:blockstart'}
              )
              . "\n";
            $blockOffset->{'functionbody'} = $function->{'swi:line:blockstart'};
        }
        else
        {
            $block->{'initial'} =
              swiSourceCodeGlobalGet( $functionsData, undef, @block_Initial );
            $blockOffset->{'initial'} = 0;
            $block->{'code'}          =
              swiSourceCodeGlobalGet( $functionsData, undef, @block_Code );
            $blockOffset->{'code'} = 0;
            $block->{'comments'}   =
              swiSourceCodeGlobalGet( $functionsData, undef, @block_Comment );
            $blockOffset->{'comments'} = 0;
            $block->{'nopreprocessor'} =
              swiSourceCodeGlobalGet( $functionsData, undef, @block_NoPrep );
            $blockOffset->{'nopreprocessor'} = 0;
            $block->{'nostrings'}            =
              swiSourceCodeGlobalGet( $functionsData, undef, @block_NoStr );
            $blockOffset->{'nostrings'} = 0;
            $block->{'purified'}        =
              swiSourceCodeGlobalGet( $functionsData, undef, $block_Purified );
            $blockOffset->{'purified'} = 0;
            $block->{'commentshead'}   =
              swiSourceCodeGlobalGet( $functionsData,
                $function->{'swi:line:headerstart'},
                @block_Comment );
            $blockOffset->{'commentshead'} = 0;
            $block->{'functionhead'}       = "";    # N/A
            $blockOffset->{'functionhead'} = 0;
            $block->{'functionbody'}       = "";    # N/A
            $blockOffset->{'functionbody'} = 0;
        }

        # Initialize container
        $function->{'swi:statistic'} = {
            'swi:length' => {
                'swi:source'        => {},
                'swi:executable'    => {},
                'swi:comment'       => {},
                'swi:blank'         => {},
                'swi:function:name' => {}
            },
            'swi:lines' => {
                'swi:source'         => {},
                'swi:executable'     => {},
                'swi:comment'        => {},
                'swi:blank'          => {},
                'swi:comment:header' => {}
            },
            'swi:complexity' => {
                'swi:cyclomatic' => {},
                'swi:blocks'     => {},
                'swi:maxdepth'   => {}
            },
            'swi:duplication' => { 'swi:symbols' => { 'swi:exact' => 0 }, },
            'swi:checksum'    => { 'swi:source'  => { 'swi:exact' => 0 }, }
        };

        $function->{'swi:reference'} = [];

        # Calculate swi:length->swi:source
        # Note: this statistic is used to detect differences
        # Global code is compared without new lines
        my $initialContent = $block->{'initial'};
        if ( $functionName eq $regexpCodeGlobalFunctionName )
        {
            $initialContent =~ s/\n+//g;
        }
        $function->{'swi:statistic'}->{'swi:length'}->{'swi:source'}
          ->{'swi:exact'} = length($initialContent);

        # Calculate swi:length->swi:executable
        $function->{'swi:statistic'}->{'swi:length'}->{'swi:executable'}
          ->{'swi:exact'} = length( $block->{'purified'} );

        # Calculate swi:length->swi:comment
        $function->{'swi:statistic'}->{'swi:length'}->{'swi:comment'}
          ->{'swi:exact'} = length( $block->{'comments'} );

        # Calculate swi:length->swi:blank
        $function->{'swi:statistic'}->{'swi:length'}->{'swi:blank'}
          ->{'swi:exact'} = swiMatchPatternCount( $block->{'initial'}, '\s' );

        # Calculate swi:length->swi:function-name
        $function->{'swi:statistic'}->{'swi:length'}->{'swi:function:name'}
          ->{'swi:exact'} = length( $block->{'functionname'} );

        # Calculate swi:lines->swi:source
        $function->{'swi:statistic'}->{'swi:lines'}->{'swi:source'}
          ->{'swi:exact'} = swiMatchPatternCount( $block->{'initial'}, '\n' );

        # Calculate swi:lines->swi:executable
        $function->{'swi:statistic'}->{'swi:lines'}->{'swi:executable'}
          ->{'swi:exact'} =
          swiMatchLinesCount( $block->{'purified'}, '[^ \t]' );

        # Calculate swi:lines->swi:comment
        $function->{'swi:statistic'}->{'swi:lines'}->{'swi:comment'}
          ->{'swi:exact'} =
          swiMatchLinesCount( $block->{'comments'}, '[^ \t]' );

        # Calculate swi:lines->swi:blank
        $function->{'swi:statistic'}->{'swi:lines'}->{'swi:blank'}
          ->{'swi:exact'} = swiMatchLinesCount( $block->{'initial'}, '^\s*$' );

        # Calculate swi:lines->swi:comment:header
        $function->{'swi:statistic'}->{'swi:lines'}->{'swi:comment:header'}
          ->{'swi:exact'} =
          $function->{'swi:line:headerstart'} -
          $function->{'swi:line:commentstart'};

        # Calculate swi:complexity->swi:cyclomatic
        $function->{'swi:statistic'}->{'swi:complexity'}->{'swi:cyclomatic'}
          ->{'swi:exact'} =
          swiMatchPatternCount(
            swiSourceCodeStringsRemove( $block->{'purified'} ),
            $regexpCodeMatch_ComplexityCyclomatic );

        # Calculate swi:complexity->swi:blocks
        # -1 in order not to count main function's block
        $function->{'swi:statistic'}->{'swi:complexity'}->{'swi:blocks'}
          ->{'swi:exact'} =
          swiMatchPatternCount( $block->{'purified'}, $regexpCodeBlockStart ) -
          1;

        # Calculate swi:complexity->swi:maxdepth
        $function->{'swi:statistic'}->{'swi:complexity'}->{'swi:maxdepth'}
          ->{'swi:exact'} = $function->{'swi:depth'};

        # Calculate swi:checksum->swi:index
        # Note: this statistic is used to detect differences
        # Global code is compared without new lines
        my @symbols = split( //, $initialContent );
        my $crcSumTotal = 0;
        for ( my $pos = 0 ; $pos <= $#symbols ; $pos++ )
        {
            $crcSumTotal =
              ( $crcSumTotal << 8 )
              ^ $crctab[ ( $crcSumTotal >> 24 ) ^ ( unpack 'C', $symbols[$pos] )
              ];
        }
        $function->{'swi:statistic'}->{'swi:checksum'}->{'swi:source'}
          ->{'swi:exact'} = $crcSumTotal;

        # Scan function by scaner tool
        foreach my $rule ( @{$scanerRules} )
        {
            if ( defined( $block->{ $rule->{'swi:codecontent'} } ) )
            {
                push(
                    @{ $function->{'swi:reference'} },
                    swiSourceCodeScan(
                        $file,
                        $blockOffset->{ $rule->{'swi:codecontent'} },
                        $block->{ $rule->{'swi:codecontent'} },
                        $rule->{'swi:searchpattern'},
                        $rule->{'swi:messagepattern'}
                    )
                );
            }
            else
            {
                STATUS(
"Wrong configuiration: 'swi:scaner/swi:rule/swi:codecontent' property is not from the acceptable set of values!"
                );
                $exitCode++;
            }

        }

        # Add to dupindexer for further processing
        if ( defined( $block->{ $dupfinderSettings->{'swi:codecontent'} } ) )
        {
            if (
                $functionName ne $regexpCodeGlobalFunctionName
                || ( defined( $dupfinderSettings->{'swi:globalcode'} )
                    && $dupfinderSettings->{'swi:globalcode'} eq 'on' )
              )
            {
                swiDupindexFunctionAdd( $file, $functionName,
                    $block->{ $dupfinderSettings->{'swi:codecontent'} } );
            }
        }
        else
        {
            STATUS(
"Wrong configuiration: 'swi:indexer:dup/swi:codecontent' property is not from the acceptable set of values!"
            );
            $exitCode++;
        }
    }

    return $functionsData;
}

#
# This function uses external tool for duplication collection
#
sub swiSourceIndexDuplicationAdd
{
    my $filesData = shift();

    STATUS("Searching for duplication...");
    print $dupindexIn "start\n";

    my $outStream = "";
    while ( defined($dupindexOut) && ( my $line = <$dupindexOut> ) )
    {
        $outStream .= $line;
    }

    my @dupdataGoups = split( /info: group_start/, $outStream );

    foreach (@dupdataGoups)
    {
        my @parsedData;
        my @dupdataSplit = split( /\n/, $_ );
        foreach (@dupdataSplit)
        {
            if ( $_ =~
m/duplication: file: '(.*)' function: '(.*)' possition: '(.*)' size: '(.*)'/
              )
            {
                $filesData->{$1}->{$2}->{'swi:statistic'}->{'swi:duplication'}
                  ->{'swi:symbols'}->{'swi:exact'} += $4;

                push(
                    @parsedData,
                    {
                        'swi:ref:type'     => 'dup',
                        'swi:dup:file'     => $1,
                        'swi:dup:function' => $2,
                        'swi:dup:line'     => $3 +
                          $filesData->{$1}->{$2}->{'swi:line:headerstart'},
                        'swi:dup:size' => $4
                    }
                );
            }
        }

        foreach my $dupData (@parsedData)
        {
            push(
                @{
                    $filesData->{ $dupData->{'swi:dup:file'} }
                      ->{ $dupData->{'swi:dup:function'} }->{'swi:reference'}
                  },
                @parsedData
            );
        }
    }

    my $errStream = "";
    while ( defined($dupindexErr) && ( my $line = <$dupindexErr> ) )
    {
        STATUS("Internal dupindex tool detected the error.");
        STATUS($line);
        STATUS("    1. Check 'swi:indexer:dup' section in configuration.");
        STATUS(
"    2. Check that swi/dupindex tool is runable on your system/platform."
        );
        STATUS("    3. Recompile swi/dupindex tool for your system/platform.");
        STATUS("    4. Report the problem to developers.");

# The final return code is unsuccessful
# It means that these errors/warnings should be fixed before the next processing
        $exitCode++;
    }

    return $filesData;
}

sub swiSourceIndexGcovAdd
{
    my $location      = shift();
    my $file          = shift();
    my $functionsData = shift();
    my $filePattern   = shift();
    my @listTmp       = $file =~ m/$filePattern/;
    my $gcdaFile      = eval( 'my $tmp = "' . shift() . '";' );

    # Add coverage statistic
    my $fh = new FileHandle( $location . "/" . $gcdaFile, "r" );
    if ( !defined($fh) )
    {
        STATUS(
"gcda file '$location/$gcdaFile' is not found  for the '$file' source."
        );

        #foreach my $functionName ( keys %{$functionsData} )
        #{
        #    $functionsData->{$functionName}->{'swi:statistic'}
        #      ->{'swi:coverage'} = {
        #        'swi:gsum:lines'     => { 'swi:exact' => 0 },
        #        'swi:gsum:branches'  => { 'swi:exact' => 0 },
        #        'swi:gsum:calls'     => { 'swi:exact' => 0 },
        #        'swi:gcov:lines'     => { 'swi:exact' => 0 },
        #        'swi:gcov:branches'  => { 'swi:exact' => 0 },
        #        'swi:gcov:takenonce' => { 'swi:exact' => 0 },
        #        'swi:gcov:calls'     => { 'swi:exact' => 0 }
        #      };
        #}
    }
    else
    {
        my $gcovCommand = "gcov -f -b $location/$gcdaFile";

        my $gcovData = `$gcovCommand`;
        $gcovData =~ s/No executable lines/Lines executed:100.OO% of O/g;
        $gcovData =~ s/No calls/Calls executed:100.00% of O/g;
        $gcovData =~
s/No branches/Branches executed:100.O0% of O\nTaken at least once:100.O0% of O/g;
        my @covData = split( "\n\n", $gcovData );

        foreach (@covData)
        {
            next if ( $_ =~ m/^File/ );
            my (
                $functionName,  $linesExec, $linesTotal, $branchesExec,
                $branchesTotal, $takenOnce, $callsExec,  $callsTotal
              )
              = ( $_ =~
m/^Function\s+\'(.*)\'\s+Lines\s+executed:(.*)%\s+of\s+(.*)\s+Branches\s+executed:(.*)%\s+of\s+(.*)\s+Taken\s+at\s+least\s+once:(.*)%\s+of\s+.*\s+Calls\s+executed:(.*)%\s+of\s+(.*)/
              );

            if ( defined( $functionsData->{$functionName} ) )
            {
                $functionsData->{$functionName}->{'swi:statistic'}
                  ->{'swi:coverage'} = {
                    'swi:gsum:lines'    => { 'swi:exact' => $linesTotal },
                    'swi:gsum:branches' => { 'swi:exact' => $branchesTotal },
                    'swi:gsum:calls'    => { 'swi:exact' => $callsTotal },
                    'swi:gcov:lines'    => {
                        'swi:exact' =>
                          swiUtil_Round( $linesExec * $linesTotal / 100 )
                    },
                    'swi:gcov:branches' => {
                        'swi:exact' =>
                          swiUtil_Round( $branchesExec * $branchesTotal / 100 )
                    },
                    'swi:gcov:takenonce' => {
                        'swi:exact' =>
                          swiUtil_Round( $takenOnce * $branchesTotal / 100 )
                    },
                    'swi:gcov:calls' => {
                        'swi:exact' =>
                          swiUtil_Round( $callsExec * $callsTotal / 100 )
                    }
                  };
            }
            else
            {
                STATUS(
"gcov reports the data for '$functionName' function but SWI parser did not detect it"
                );
                $exitCode++;
            }
        }
    }
}

sub swiSourceCodeParse
{
    my $file         = shift();
    my $blockCode    = shift();
    my @blockComment = split( "\n", shift() );

    @blockComment =
      swiUtilArrayExtend( [@blockComment],
        swiMatchPatternCount( $blockCode, '\n' ) + 1, "" );

    my $result    = {};
    my $deepLevel = 0;

    if ( swiMatchPatternCount( $blockCode, $regexpCodeBlockStart ) !=
        swiMatchPatternCount( $blockCode, $regexpCodeBlockEnd ) )
    {
        PRINT( $file, 0, "error",
            "Mismatch in number of start/end of blocks delimeters!\n" );
        DEBUG("The code before parsing:\n$blockCode");
        return $result;
    }

    my $posPrev      = 0;
    my $posCurrent   = 0;
    my $isInFunction = 0;
    my $currentFunc  = undef;
    my $currentLine  = 0;
    my $currentPos   = 0;
    my $currentDepth = 0;
    my @containers;

    while ( $blockCode =~ m/($regexpCodeBlockStart)|($regexpCodeBlockEnd)/g )
    {
        $posPrev    = $posCurrent;
        $posCurrent = pos($blockCode);

        my $matchPre  = $`;
        my $matchStr  = $&;
        my $matchPost = $';

        my $blockFragFull =
          substr( $blockCode, $posPrev, $posCurrent - $posPrev );
        $currentLine += swiMatchPatternCount( $blockFragFull, "\n" );
        $currentPos  += length($blockFragFull);

        if ( $matchStr =~ m/^$regexpCodeBlockStart$/ )
        {
            my $blockFragLast = $blockFragFull;
            $blockFragLast =~ s/^($regexpCodeStatements)*\s*//;

            # opened block detected
            $deepLevel++;

            if ( $isInFunction == 0 )
            {

                # Check whether it is a function start
                if ( $blockFragLast =~
m/^($regexpCodeFunctionModifier)*($regexpCodeFunctionIdentifier)($regexpCodeFunctionArguments)($regexpCodeBlockStart)$/
                  )
                {
                    my $matchedHeader = $&;
                    my $mod           = $1;
                    my $word          = $2;

                    if ( !defined($mod) )
                    {
                        $mod = "";
                    }

                    # Remove empty symbols in header
                    $matchedHeader =~ s/^\s*//;

                    # Check if modifier consumes something from identifier
                    # and return back the last part from modifier to identifier
                    ( $mod . $word ) =~ m/$regexpCodeFunctionIdentifier$/;
                    $mod  = $`;
                    $word = $&;

                    # Remove empty symbols in identifier
                    $word =~ s/\s+$//;
                    $word =~ s/[\n\t ]+/ /g;
                    $word =~
s/\s*$regexpCodeContainerDelimeter\s*/$regexpCodeContainerDelimeter/;

                    # Remove empty symbols in modifier
                    $mod =~ s/^\s*//;
                    $mod =~ s/\s*$//;
                    $mod =~ s/[\n\t ]+/ /g;

                    if ( $word !~ m/^($regexpCodeKeyword)$/ )
                    {
                        $isInFunction = $deepLevel;

                        # Attach containers to the name of function
                        foreach my $container ( reverse @containers )
                        {
                            if ( defined($container) )
                            {
                                $word = $container
                                  . $regexpCodeContainerDelimeter
                                  . $word;
                            }
                        }

                        # Add the code before the block start
                        # (name of function, arguments, ..)
                        my $matchedHeaderLinesNum =
                          swiMatchPatternCount( $matchedHeader, "\n" );

                        # Check if there are comments before the header
                        my $consumedTopLines = 1;
                        while (
                            $currentLine - $matchedHeaderLinesNum -
                            $consumedTopLines >= 0
                            && $blockComment[
                            $currentLine - $matchedHeaderLinesNum -
                            $consumedTopLines
                            ] !~ m/^\s*$/
                          )
                        {
                            $consumedTopLines++;
                        }

                        if ( defined( $result->{$word} ) )
                        {
                            PRINT( $file, $currentLine + 1, 'debug',
"The same function detected more than once: '$word'"
                            );
                            my $counter = 2;
                            while (
                                defined(
                                    $result->{ $word . " (" . $counter . ")" }
                                )
                              )
                            {
                                $counter++;
                            }
                            $word .= " (" . $counter . ")";
                        }

                        # Store data in result
                        $currentFunc = $word;
                        $result->{$word} = {
                            'swi:pos:blockstart'  => $currentPos,
                            'swi:pos:headerstart' => $currentPos -
                              length($matchedHeader),
                            'swi:pos:blockend'     => undef,
                            'swi:line:blockstart'  => $currentLine,
                            'swi:line:headerstart' => $currentLine -
                              $matchedHeaderLinesNum,
                            'swi:line:commentstart' => $currentLine -
                              $matchedHeaderLinesNum -
                              ( $consumedTopLines - 1 ),
                            'swi:line:blockend' => undef,
                            'swi:modifier'      => $mod,
                            'swi:indent'        => $deepLevel
                        };

                        PRINT( $file, $currentLine + 1, 'debug',
                            "Function detected: '$word', with modifier: '$mod'"
                        );
                    }
                }

                # Check whether it is a container start
                elsif ( $blockFragLast =~
m/^($regexpCodeContainerModifier)\s+($regexpCodeContainerIdentifier)($regexpCodeContainerArguments)($regexpCodeBlockStart)$/
                  )
                {
                    my $mod  = $1;
                    my $word = $2;
                    $mod =~ s/^\s*//;
                    $mod =~ s/\s*$//;
                    $mod =~ s/[\n\t ]+/ /g;
                    if ( $word !~ m/^$regexpCodeKeyword$/ )
                    {
                        PRINT( $file, $currentLine + 1, 'debug',
                            "Container detected: '$word', with modifier: '$mod'"
                        );
                        $containers[ $deepLevel - 1 ] = $word;
                    }
                }

                # Check if block start should be ignored
                elsif ( $blockFragLast =~
                    m/($regexpCodeBlockStartIgnore)($regexpCodeBlockStart)$/ )
                {
                    PRINT( $file, $currentLine + 1,
                        'debug', "Block start delimeter ignored/missed: '$&'" );
                }
                elsif ( $blockFragLast =~ m/^\s*($regexpCodeBlockStart)$/ )
                {
                    PRINT( $file, $currentLine + 1, 'debug',
                        "Empty code before block start delimeter detected: '$&'"
                    );
                }
                else
                {
                    $blockFragLast =~ s/^\s*//;
                    PRINT( $file, $currentLine + 1,
                        'error',
                        "Unknown type of started block: '$blockFragLast'" );
                    $exitCode++;
                }
            }
            else
            {

                # Calculate maximum indent level
                if ( $currentDepth < $deepLevel - $isInFunction )
                {
                    $currentDepth = $deepLevel - $isInFunction;
                }
            }
        }
        else
        {

            if ($deepLevel <= 0)
            {
                PRINT( $file, $currentLine + 1,
                        'error',
                        "Mismatched closing of a block. The file is not processed completely!" );
                $exitCode++;
                return $result;
            }

            # block closer detected
            if ( $deepLevel == $isInFunction )
            {
                $isInFunction                                  = 0;
                $result->{$currentFunc}->{'swi:pos:blockend'}  = $currentPos;
                $result->{$currentFunc}->{'swi:line:blockend'} = $currentLine;
                $result->{$currentFunc}->{'swi:depth'}         = $currentDepth;
                $currentDepth                                  = 0;
                $currentFunc                                   = undef;
            }
            $containers[ $deepLevel - 1 ] = undef;
            $deepLevel--;
        }
    }

    # Initialize GLOBAL function
    $result->{$regexpCodeGlobalFunctionName} = {
        'swi:pos:blockstart'    => 0,    # not used
        'swi:pos:headerstart'   => 0,    # not used
        'swi:pos:blockend'      => 0,    # not used,
        'swi:line:blockstart'   => 0,    # not used
        'swi:line:headerstart'  => 0,    # used to deattach header with comments
        'swi:line:commentstart' => 0,    # not used
        'swi:line:blockend'     => 0,    # not used
        'swi:modifier'          => "",   # not used
        'swi:indent'            => 0,    # not used
        'swi:depth'             => 0     # not used
    };
    for ( my $i = 0 ; $i <= $#blockComment ; ++$i )
    {
        $result->{$regexpCodeGlobalFunctionName}->{'swi:line:headerstart'} = $i;
        if ( $blockComment[$i] =~ m/^\s*$/ )
        {

            # Empty line detected => header end matched
            last;
        }
    }

    return $result;
}

sub swiSourceCodeStringsRemove
{
    my $code   = shift();
    my $result = "";

    my $posPrev              = 0;
    my $posCurrent           = 0;
    my $isInString           = 0;
    my $lastPart             = $code;
    my $borderPatternDynamic = $regexpCodeStringBorder_Text;

    while ( $code =~ m/$borderPatternDynamic/g )
    {
        $posPrev    = $posCurrent;
        $posCurrent = pos($code);

        my $matchPre  = $`;
        my $matchStr  = $&;
        my $matchPost = $';
        $lastPart = "";

        my $blockFrag =
          substr( $code, $posPrev, $posCurrent - $posPrev - length($matchStr) );

        if ( $isInString == 0 )
        {
            $result .= $blockFrag . $matchStr;
            $isInString           = 1;
            $borderPatternDynamic = $matchStr;
        }
        else
        {
            if ( ( $blockFrag . $matchStr ) =~
                m/($regexpCodeStringBorder_Escape)($borderPatternDynamic)$/ )
            {

                # This string border should be ignored
                $blockFrag =~ s/[^\n]//g;
                $result .= $blockFrag;
            }
            else
            {

                # Save last part only if string end detected;
                $lastPart = $matchPost;

                # Keep newlines in the code inside strings
                $blockFrag =~ s/[^\n]//g;
                $result .= $blockFrag;
                $result .= $matchStr;
                $isInString           = 0;
                $borderPatternDynamic = $regexpCodeStringBorder_Text;
            }
        }
    }

    return $result . $lastPart;
}

sub swiSourceCodePreprocessorRemove
{
    my $code      = shift();
    my $result    = "";
    my @codeLines = swiUtilArrayExtend( [ split( "\n", $code ) ],
        swiMatchPatternCount( $code, '\n' ) - 1, "" );

    my $isInPreprocessor = 0;

    foreach my $line (@codeLines)
    {

        if (   $isInPreprocessor == 1
            || $line =~ m/$regexpCodePreprocessorStart/ )
        {
            $isInPreprocessor = 1;

            # Just add empty line
            $result .= "\n";

            if ( $line =~ m/$regexpCodePreprocessorEnd/ )
            {
                $isInPreprocessor = 0;
            }
        }
        else
        {
            $line =~ s/\n//g;
            $result .= $line . "\n";
        }
    }

    return $result;
}

sub swiSourceCommentsDeattach
{
    my @fileLines = @_;

    my $blockAll          = "";
    my $blockCode         = "";
    my $blockComment      = "";
    my $countLinesAll     = 0;
    my $countLinesCode    = 0;
    my $countLinesComment = 0;
    my $isInCode          = 1;

    foreach my $line (@fileLines)
    {
        if ( $isInCode == 1 )
        {
            if ( $line =~
                m/(($regexpCommentMultiStart)|($regexpCommentSingle))/ )
            {
                my $matchPre  = $`;
                my $matchStr  = $&;
                my $matchPost = $';

                my $marker = "#@%" . int( rand(0xFF) ) . "%@#";
                if ( swiSourceCodeStringsRemove( $matchPre . $marker ) !~
                    m/$marker/ )
                {

                    # This block ends inside the string
                    # i.e. comment start marker detected inside the string
                    # Process again the string with removed comment start marker
                    $line =~
                      s/(($regexpCommentMultiStart)|($regexpCommentSingle))//;
                    $fileLines[$countLinesAll] = $line;
                    redo;
                }
                elsif ( $matchStr =~ m/^$regexpCommentMultiStart$/ )
                {

                    # Get the code before the comment
                    $blockCode .= $matchPre;
                    $blockAll  .= $matchPre;

                    $isInCode = 0;
                    $blockComment .= $matchStr;
                    $blockAll     .= $matchStr;

                    # Process again the last fragment
                    $fileLines[$countLinesAll] = $matchPost;
                    $line = $matchPost;
                    redo;
                }
                else
                {

                    # Get the code before the comment
                    $blockCode .= $matchPre;
                    $blockAll  .= $matchPre;

                    # Single line comment detected
                    $matchPost =~ s/\n//g;
                    $blockComment .= $matchStr . $matchPost;
                    $blockAll     .= $matchStr . $matchPost;
                }
            }
            else
            {
                $line =~ s/\n//g;
                $blockCode .= $line;
                $blockAll  .= $line;
            }
        }
        else
        {

            # Check multi line comment end
            if ( $line =~ m/$regexpCommentMultiEnd/ )
            {
                my $matchPre  = $`;
                my $matchStr  = $&;
                my $matchPost = $';

                # Get the code before the comment
                $blockComment .= $matchPre . $matchStr;
                $blockAll     .= $matchPre . $matchStr;

                $isInCode = 1;

                # Process again the last fragment
                $fileLines[$countLinesAll] = $matchPost;
                $line = $matchPost;
                redo;
            }
            else
            {
                $line =~ s/\n//g;
                $blockComment .= $line;
                $blockAll     .= $line;
            }
        }

        $blockCode    .= "\n";
        $blockComment .= "\n";
        $blockAll     .= "\n";
        $countLinesAll++;
    }

    return ( $blockAll, $blockCode, $blockComment );
}

sub swiMatchPatternCount
{
    my $text    = shift();
    my $pattern = shift();
    my $count   = 0;

    $count = () = $text =~ m/$pattern/g;
    
    return $count;
}

sub swiMatchLinesCount
{
    my @text    = split( "\n", shift() );
    my $pattern = shift();
    my $count   = 0;

    foreach (@text)
    {
        if ( $_ =~ m/$pattern/ )
        {
            $count++;
        }
    }
    return $count;
}

sub swiUtilArrayExtend
{
    my $array       = shift();
    my $finalLength = shift();
    my $emptySymbol = shift();

    if ( $#{$array} > $finalLength )
    {
        DEBUG( "Length of array: " . $#{$array} );
        DEBUG( "Requested final length: " . $finalLength );
        DEBUG( Dumper($array) );
        die('Internal Error occured!');
    }

    while ( $finalLength - $#{$array} > 0 )
    {
        push( @{$array}, $emptySymbol );
    }

    return @{$array};
}

sub swiUtilDirectoryCleanUp
{
    my $dir = shift();
    die("Internal error!") if not defined $dir;
    die("Internal error!") if $dir eq "";
    die("Internal error!") if $dir eq ".";
    die("Internal error!") if $dir eq "./";

    if ( opendir( DIR, $dir ) )
    {
        while ( my $file = readdir(DIR) )
        {
            unlink $dir . "/" . $file;
        }
        closedir(DIR);
    }
}

sub swiUtil_Round
{
    my $float = shift();
    if ( ( $float - int($float) ) > 0.5 )
    {
        return int( $float + 1.0 );
    }
    else
    {
        return int($float);
    }
}

return 1;
