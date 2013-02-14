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
package Internal::Output;

use strict;

require Exporter;
use vars qw($VERSION @ISA @EXPORT @EXPORT_OK $PREFERRED_PARSER);
@ISA              = qw(Exporter);
@EXPORT           = qw(DEBUG_ENABLED DEBUG STATUS PRINT);
@EXPORT_OK        = qw(DEBUG_ENABLED DEBUG STATUS PRINT);
$VERSION          = '1.0';
$PREFERRED_PARSER = undef;

#
# Global variables
#
my $globalDebugEnabled = 0;

#
# Interfaces to get/set internal variables
#

sub DEBUG_ENABLED
{
    if (@_)
    {
        $globalDebugEnabled = shift();
    }
    return $globalDebugEnabled;
}

#
# Interfaces to dump/print/publish the information
#

sub DEBUG
{
    my $text = shift();
    if ( $globalDebugEnabled != 0 )
    {
        print "[SWI DEBUG  MESSAGE]: $text\n";
    }
}

sub STATUS
{
    my $text = shift();
    
    print "[SWI STATUS MESSAGE]: $text\n";
}

sub PRINT
{
    my $file = shift();
    my $line = shift();
    my $severity = shift();
    my $text = shift();
    
    $severity = lc $severity;
    
    if ( $severity ne 'debug' || $globalDebugEnabled != 0 )
    {
        if ($severity eq 'debug')
        {
            print STDOUT "$file:$line: $severity: $text\n";
        }
        elsif($severity eq 'error' || $severity eq 'warning' || $severity eq 'notice' || $severity eq 'info')
        {
            print STDERR "$file:$line: $severity: $text\n";
        }
    }
}

return 1;