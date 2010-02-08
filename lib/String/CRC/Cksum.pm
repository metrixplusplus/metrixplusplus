
package String::CRC::Cksum;

#use 5.6.1;
use strict;
use warnings;
use Carp;

require Exporter;
our @ISA = qw(Exporter);
our @EXPORT_OK = qw(cksum);
our @EXPORT = qw();
our $VERSION = '0.03';

use fields qw(cksum size);

my @crctab = (
    0x00000000,
    0x04c11db7, 0x09823b6e, 0x0d4326d9, 0x130476dc, 0x17c56b6b, 0x1a864db2, 0x1e475005, 0x2608edb8, 0x22c9f00f, 0x2f8ad6d6,
    0x2b4bcb61, 0x350c9b64, 0x31cd86d3, 0x3c8ea00a, 0x384fbdbd, 0x4c11db70, 0x48d0c6c7, 0x4593e01e, 0x4152fda9, 0x5f15adac,
    0x5bd4b01b, 0x569796c2, 0x52568b75, 0x6a1936c8, 0x6ed82b7f, 0x639b0da6, 0x675a1011, 0x791d4014, 0x7ddc5da3, 0x709f7b7a,
    0x745e66cd, 0x9823b6e0, 0x9ce2ab57, 0x91a18d8e, 0x95609039, 0x8b27c03c, 0x8fe6dd8b, 0x82a5fb52, 0x8664e6e5, 0xbe2b5b58,
    0xbaea46ef, 0xb7a96036, 0xb3687d81, 0xad2f2d84, 0xa9ee3033, 0xa4ad16ea, 0xa06c0b5d, 0xd4326d90, 0xd0f37027, 0xddb056fe,
    0xd9714b49, 0xc7361b4c, 0xc3f706fb, 0xceb42022, 0xca753d95, 0xf23a8028, 0xf6fb9d9f, 0xfbb8bb46, 0xff79a6f1, 0xe13ef6f4,
    0xe5ffeb43, 0xe8bccd9a, 0xec7dd02d, 0x34867077, 0x30476dc0, 0x3d044b19, 0x39c556ae, 0x278206ab, 0x23431b1c, 0x2e003dc5,
    0x2ac12072, 0x128e9dcf, 0x164f8078, 0x1b0ca6a1, 0x1fcdbb16, 0x018aeb13, 0x054bf6a4, 0x0808d07d, 0x0cc9cdca, 0x7897ab07,
    0x7c56b6b0, 0x71159069, 0x75d48dde, 0x6b93dddb, 0x6f52c06c, 0x6211e6b5, 0x66d0fb02, 0x5e9f46bf, 0x5a5e5b08, 0x571d7dd1,
    0x53dc6066, 0x4d9b3063, 0x495a2dd4, 0x44190b0d, 0x40d816ba, 0xaca5c697, 0xa864db20, 0xa527fdf9, 0xa1e6e04e, 0xbfa1b04b,
    0xbb60adfc, 0xb6238b25, 0xb2e29692, 0x8aad2b2f, 0x8e6c3698, 0x832f1041, 0x87ee0df6, 0x99a95df3, 0x9d684044, 0x902b669d,
    0x94ea7b2a, 0xe0b41de7, 0xe4750050, 0xe9362689, 0xedf73b3e, 0xf3b06b3b, 0xf771768c, 0xfa325055, 0xfef34de2, 0xc6bcf05f,
    0xc27dede8, 0xcf3ecb31, 0xcbffd686, 0xd5b88683, 0xd1799b34, 0xdc3abded, 0xd8fba05a, 0x690ce0ee, 0x6dcdfd59, 0x608edb80,
    0x644fc637, 0x7a089632, 0x7ec98b85, 0x738aad5c, 0x774bb0eb, 0x4f040d56, 0x4bc510e1, 0x46863638, 0x42472b8f, 0x5c007b8a,
    0x58c1663d, 0x558240e4, 0x51435d53, 0x251d3b9e, 0x21dc2629, 0x2c9f00f0, 0x285e1d47, 0x36194d42, 0x32d850f5, 0x3f9b762c,
    0x3b5a6b9b, 0x0315d626, 0x07d4cb91, 0x0a97ed48, 0x0e56f0ff, 0x1011a0fa, 0x14d0bd4d, 0x19939b94, 0x1d528623, 0xf12f560e,
    0xf5ee4bb9, 0xf8ad6d60, 0xfc6c70d7, 0xe22b20d2, 0xe6ea3d65, 0xeba91bbc, 0xef68060b, 0xd727bbb6, 0xd3e6a601, 0xdea580d8,
    0xda649d6f, 0xc423cd6a, 0xc0e2d0dd, 0xcda1f604, 0xc960ebb3, 0xbd3e8d7e, 0xb9ff90c9, 0xb4bcb610, 0xb07daba7, 0xae3afba2,
    0xaafbe615, 0xa7b8c0cc, 0xa379dd7b, 0x9b3660c6, 0x9ff77d71, 0x92b45ba8, 0x9675461f, 0x8832161a, 0x8cf30bad, 0x81b02d74,
    0x857130c3, 0x5d8a9099, 0x594b8d2e, 0x5408abf7, 0x50c9b640, 0x4e8ee645, 0x4a4ffbf2, 0x470cdd2b, 0x43cdc09c, 0x7b827d21,
    0x7f436096, 0x7200464f, 0x76c15bf8, 0x68860bfd, 0x6c47164a, 0x61043093, 0x65c52d24, 0x119b4be9, 0x155a565e, 0x18197087,
    0x1cd86d30, 0x029f3d35, 0x065e2082, 0x0b1d065b, 0x0fdc1bec, 0x3793a651, 0x3352bbe6, 0x3e119d3f, 0x3ad08088, 0x2497d08d,
    0x2056cd3a, 0x2d15ebe3, 0x29d4f654, 0xc5a92679, 0xc1683bce, 0xcc2b1d17, 0xc8ea00a0, 0xd6ad50a5, 0xd26c4d12, 0xdf2f6bcb,
    0xdbee767c, 0xe3a1cbc1, 0xe760d676, 0xea23f0af, 0xeee2ed18, 0xf0a5bd1d, 0xf464a0aa, 0xf9278673, 0xfde69bc4, 0x89b8fd09,
    0x8d79e0be, 0x803ac667, 0x84fbdbd0, 0x9abc8bd5, 0x9e7d9662, 0x933eb0bb, 0x97ffad0c, 0xafb010b1, 0xab710d06, 0xa6322bdf,
    0xa2f33668, 0xbcb4666d, 0xb8757bda, 0xb5365d03, 0xb1f740b4
);


sub new {
    my $class = shift;
    my String::CRC::Cksum $self = fields::new(ref $class || $class);
    return $self->reset;
}   # new


sub reset {
    my String::CRC::Cksum $self = shift;
    $self->{cksum} = $self->{size} = 0;
    return $self;
}   # reset


sub add {
    use integer;
    my String::CRC::Cksum $self = shift;
    my $cksum = $self->{cksum};
    my $size = $self->{size};

    while(@_) {
        my $n = length $_[0];

        for(my $i = 0; $i < $n; ++$i) {
            my $c = unpack 'C', substr $_[0], $i, 1;
            $cksum = ($cksum << 8) ^ $crctab[($cksum >> 24) ^ $c];
            ++$size;
        }

    }
    continue { shift }

    $self->{cksum} = $cksum;
    $self->{size} = $size;

    return $self;
}   # add


sub addfile {
    my String::CRC::Cksum $self = shift;
    my $stat;

    local $_;
    while(my $ifd = shift) {
        $self->add($_) while $stat = read $ifd, $_, 4096;

        if(! defined $stat) {
            croak "error reading from filehandle: $!";
        }
    }

    return $self;
}   # addfile


sub peek {
    use integer;
    my String::CRC::Cksum $self = shift;
    my $cksum = $self->{cksum};
    my $size = $self->{size};

    # Extend with the length of the data
    while($size != 0) {
        my $c = $size & 0377;
        $size >>= 8;
        $cksum = ($cksum << 8) ^ $crctab[($cksum >> 24) ^ $c];
    }
    $cksum = ~ $cksum;

    no integer;
    my $crc = $cksum;
    $crc += 4294967296 if $crc < 0;

    return wantarray ? ($crc, $self->{size}) : $crc;

}   # addfile


sub result {
    my String::CRC::Cksum $self = shift;
    my ($cksum, $size) = $self->peek;
    $self->reset;
    return wantarray ? ($cksum, $size) : $cksum;
}   # result


sub cksum(@) {
    my $sum = String::CRC::Cksum->new;

    while(@_) {
        if(ref $_[0])
            { $sum->addfile($_[0]) }
        else
            { $sum->add($_[0]) }
    }
    continue { shift }

    return $sum->result;
}   # cksum

1;

__END__

=head1 NAME

String::CRC::Cksum - Perl extension for calculating checksums
in a manner compatible with the POSIX cksum program.

=head1 SYNOPSIS

B<OO style>:
  use String::CRC::Cksum;

  $cksum = String::CRC::Cksum->new;
  $cksum1 = $cksum->new;     # clone (clone is reset)

  $cksum->add("string1");
  $cksum->add("string2");
  $cksum->add("string3", "string4", "string5", ...);
  ...
  ($cksum, $size) = $cksum->peek;
  $cksum->add("string6", ...);
  ...
  ($cksum, $size) = $cksum->result;

  $cksum1->addfile(\*file1);     # note: adding many files
  $cksum1->addfile(\*file2);     # is probably a silly thing
  $cksum1->addfile(\*file3);     # to do, but you *could*...
  ...

B<Functional style>:
  use String::CRC::Cksum qw(cksum);

  $cksum = cksum("string1", "string2", ...);

  ($cksum, $size) = cksum("string1", "string2", ...);

  $cksum = cksum(\*FILE);

  ($cksum, $size) = cksum(\*FILE);

=head1 DESCRIPTION

The String::CRC::Cksum module calculates a 32 bit CRC,
generating the same CRC value as the POSIX cksum program.
If called in a list context, returns the length of the data
object as well, which is useful for fully emulating
the cksum program. The returned checksum will always be
a non-negative integral number in the range 0..2^32-1.

Despite its name, this module is able to compute the
checksum of files as well as of strings.
Just pass in a reference to a filehandle,
or a reference to any object that can respond to
a read() call and eventually return 0 at "end of file".

Beware: consider proper use of binmode()
if you are on a non-UNIX platform
or processing files derived from other platforms.

The object oriented interface can be used
to progressively add data into the checksum
before yielding the result.

The functional interface is a convenient way
to get a checksum of a single data item.

None of the routines make local copies of passed-in strings
so you can safely Cksum large strings safe in the knowledge
that there won't be any memory issues.

Passing in multiple files is acceptable,
but perhaps of questionable value.
However I don't want to hamper your creativity...

=head1 FUNCTIONS                                                        

The following functions are provided
by the "String::CRC::Cksum" module.
None of these functions are exported by default.

=over 4

=item B<new()>

Creates a new String::CRC::Cksum object
which is in a reset state, ready for action.
If passed an existing String::CRC::Cksum object,
it takes only the class -
ie yields a fresh, reset object.

=item B<reset()>

Resets the Cksum object to the intialized state.
An interesting phenomenom is,
the CRC is not zero but 0xFFFFFFFF
for a reset Cksum object.
The returned size of a reset item will be zero.

=item B<add("string", ...)>

Progressively inject data into the Cksum object
prior to requesting the final result.

=item B<addfile(\*FILE, ...)>

Progressively inject all (remaining) data from the file
into the Cksum object prior to requesting the final result.
The file handle passed in
need only respond to the read() function to be usable,
so feel free to pass in IO handles as needed.
[hmmm - methinks I should have a test for that]

=item B<peek($)>

Yields the CRC checksum
(and optionally the total size in list context)
but does not reset the Cksum object.
Repeated calls to peek() may be made
and more data may be added.

=item B<result($)>

Yields the CRC checksum
(and optionally the total size in list context)
and then resets the Cksum object.

=item B<cksum(@)>

A convenient functional interface
that may be passed a list of strings and filehandles.
It will instantiate a Cksum object,
apply the data and return the result
in one swift, sweet operation.
See how much I'm looking after you?

NOTE: the filehandles must be passed as \*FD
because I'm detecting a file handle using the ref() function.
Therefore any blessed IO handle will also satisfy ref()
and be interpreted as a file handle.

=back

=head2 EXPORT

None by default.

=head1 SEE ALSO

manpages: cksum(1) or cksum(C) depending on your flavour of UNIX.

http://www.opengroup.org/onlinepubs/007904975/utilities/cksum.html

=head1 AUTHOR

Andrew Hamm, E<lt>ahamm@cpan.orgE<gt>.

=head1 COPYRIGHT AND LICENSE

Copyright disclaimed 2003 by Andrew Hamm

This library is free software; you can redistribute it and/or modify
it under the same terms as Perl itself.

Since I collected the algorithm
from the Open Group web pages,
they might have some issues but I doubt it.
Let better legal minds than mine
determine the issues if you need.
[hopefully the CPAN and PAUSE administrators and/or testers
will understand the issues better,
and will replace this entire section
with something reasonable - hint hint.]

=cut
