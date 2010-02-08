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

use strict;
use Cwd qw(abs_path);

$0 =~ m/(.*)swi_main.pl$/;
my $globalRootDirectory      = abs_path($1);

push(@INC, "$globalRootDirectory/lib");
require SWI::Launcher;

exit swiLaunch($globalRootDirectory, @ARGV);
