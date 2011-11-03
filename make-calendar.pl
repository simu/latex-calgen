#!/usr/bin/perl
# make-calendar: ncal-Ausgabe für Latex aufbereiten

my $year = shift;

open HEAD,"< head.tex" or die "Cannot find 'head.tex': $!";
while(<HEAD>) { print; }
close HEAD;

foreach my $month (1 .. 12) {
	my ($head, @cal) = `LC_ALL=de_CH.utf8 cal $month $year`;
	my ($lines, $height) = (0,0);
	($head) = $head =~ /(\S+)/;
#	$head =~ s/(\S+)/\U$1/;
#	if($head eq "MäRZ") { $head = "MÄRZ"; }
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
	foreach (@cal) {
		chomp;
		next if /^\s*$/;
		@days = unpack '(A3)7', $_;
		$so = pop @days;
		$so = "\\textcolor\{socol\}\{$so}";
		push @days, $so;
		if($days[0] eq 'Mo') {
			print join('&', @days), "\\\\\n" if @days;
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
