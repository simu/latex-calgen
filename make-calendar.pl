#!/usr/bin/perl
# make-calendar.pl: glue ncal output into LaTeX document.

my $year = shift;
my $week_start=shift;
# cleanup week start argument
$week_start="-M" if not $week_start =~ /-S|-M/;
my $week_starts_on_sunday=$week_start eq '-S';

open HEAD,"< head.tex.in" or die "Cannot find 'head.tex.in': $!";
while(<HEAD>) { s/%year%/$year/; print; }
close HEAD;

foreach my $month (1 .. 12) {
	my ($head, @cal) = `ncal $week_start -b $month $year`;
	my ($lines, $height) = (0,0);
	($head) = $head =~ /(\S+)/;
	printf qq|\\begin{calmonth}{%s}{%d}\n|, $head, $year;
	print "\\hline\n";
	foreach (@cal) {
		chomp;
		if (/^\s*$/) {
			print STDERR "ignoring empty line\n";
			next;
		}
		$lines++;
	}
	$lines-=1;
	if($lines==5) { $height = 2.5; }
	elsif($lines==6) { $height = 1.9; }
	elsif($lines==4) { $height = 3; }
	print STDERR $height;
	print STDERR "\n";
	# first line is weekday names
	$weekdays=1;
	foreach (@cal) {
		chomp;
		next if /^\s*$/;
		@days = unpack '(A3)7', $_;
		$so=$days[$week_starts_on_sunday?0:6];
		$days[$week_starts_on_sunday?0:6]="\\textcolor\{socol\}\{$so}";
		if($weekdays) {
			print join('&', @days), "\\\\\n" if @days;
			$weekdays=0;
		}
		else {
			print join('&', @days), "\\\\[${height}cm]\n" if @days;
		}
		print "\\hline\n";
	}
	print qq|\\end{calmonth}\n|;
}

print '\end{document}';
print "\n";
