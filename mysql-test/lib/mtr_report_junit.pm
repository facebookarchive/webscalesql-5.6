# -*- cperl -*-
# Copyright (c) 2012 Twitter, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# This is a library file used by the Perl version of mysql-test-run,
# and is part of the translation of the Bourne shell script with the
# same name.

package mtr_report_junit;

use strict;
use warnings;
use Sys::Hostname;
use POSIX qw(strftime);
use base qw(Exporter);

our @EXPORT= qw(mtr_report_stats_junit mtr_junit_supported);

#
# Function: mtr_report_stats_junit
#
# Arg 1: $tests      Arrayref of completed tests
# Arg 2: $filename   File to write XML output to
# Arg 3: $package    Package to use when writing <testsuite> blocks
#
# This function acts much like mtr_report_stats from the mtr_report.pm library,
# except that instead of writing a summary of tests to STDOUT, it writes JUnit
# style XML to $filename.  This is the only exported function from this library.
#
sub mtr_report_stats_junit {
  my $tests    = shift;
  my $filename = shift;
  my $package  = shift;
  my $testinfo;
  my $doc;

  eval "use XML::Simple";
  return undef if $@;

  foreach my $tinfo (@$tests) {
    my $suite;

    if ($tinfo->{name} =~ /^([^\.]+)\./) {
      $suite = $1;
    } else {
      $suite = 'report';
    }

    $suite = "$package.$suite" if $package;

    $testinfo->{$suite}{tot_tests}++;
    $testinfo->{$suite}{tot_failed}++  if $tinfo->{failures};
    $testinfo->{$suite}{tot_skipped}++ if $tinfo->{skip};
    $testinfo->{$suite}{tot_passed}++  if $tinfo->{result} eq 'MTR_RES_PASSED';
    push (@{$testinfo->{$suite}{tests}}, $tinfo);
  }

  foreach my $suite (keys %$testinfo) {
    my $suitetime = 0;
    my @testcases;

    foreach my $tinfo (@{$testinfo->{$suite}{tests}}) {
      my $name = $tinfo->{shortname} ? $tinfo->{shortname} : $tinfo->{name};
      $name .= '_' . $tinfo->{combination} if $tinfo->{combination};

      my $testtime = $tinfo->{timer} ? $tinfo->{timer} / 1000 : 0;
      $suitetime += $testtime;

      my $testcase = gen_testcase ($name, $tinfo->{name}, $testtime);
      if ($tinfo->{failures}) {
	my $content = $tinfo->{logfile};
	$content .= "\n" . $tinfo->{comment} if $tinfo->{comment};
	my $failure = gen_failure ($tinfo->{result}, "Test failed", $content);
	push @{$testcase->{failure}}, $failure;
      }

      if ($tinfo->{skip}) {
	my $message = $tinfo->{comment} ? $tinfo->{comment} : 'unknown reason';
        # Failures and skips have the same structure
	my $skipped = gen_failure ($tinfo->{result}, $message, $message);
	push @{$testcase->{skipped}}, $skipped;
      }
      push @testcases, $testcase;
    }

    my $tot_failed = $testinfo->{$suite}{tot_failed} ?
      $testinfo->{$suite}{tot_failed} : 0;

    my $tot_skipped = $testinfo->{$suite}{tot_skipped} ?
      $testinfo->{$suite}{tot_skipped} : 0;

    my $testsuite = gen_testsuite (
      $suite,
      $suitetime,
      $tot_failed,
      $tot_skipped,
      $testinfo->{$suite}{tot_tests}
    );
    $testsuite->{package} = $package if $package;
    push @{$testsuite->{testcase}}, @testcases;
    push @{$doc->{testsuite}}, $testsuite;
  }
  my $xs = XML::Simple->new(NoEscape => 1);
  $xs->XMLout ($doc, RootName => 'testsuites', OutputFile => $filename)
}

#
# Function: mtr_junit_supported
#
# Returns true if XML output is supported (requires XML::Simple)
#
sub mtr_junit_supported {
  eval "use XML::Simple";
  return $@ ? 0 : 1;
}

#
# Function gen_testsuite
#
# Arg 1: $name      Name of the testsuite
# Arg 2: $time      Aggregate time (in seconds) of every test in the suite
# Arg 3: $failures  Number of tests that failed in the suite
# Arg 4: $skip      Number of tests that were skipped in the suite
# ARg 5: $tests     Total number of tests in the suite
#
# This function populates and returns a hashref that represents a JUnit
# <testsuite></testsuite> XML block.
#
sub gen_testsuite {
  my $name     = shift;
  my $time     = shift;
  my $failures = shift;
  my $skip     = shift;
  my $tests    = shift;
  my $hostname = hostname;

  chomp $hostname;

  return {
    name         => $name,
    hostname     => $hostname,
    errors       => 0,
    failures     => $failures,
    skip         => $skip,
    tests        => $tests,
    'time'       => $time,
    testcase     => [],
    timestamp    => strftime ("%Y-%m-%dT%H:%M:%S", localtime),
    'system-out' => [],
  };
}

#
# Function: gen_testcase
#
# Arg 1: $name   Name of the test case (must be unique)
# Arg 2: $class  Class of the test case
# Arg 3: $time   Time (in seconds) the test case took to run
#
# This function populates and returns a hashref that represents a JUnit
# <testcase></testcase> XML block.
#
sub gen_testcase {
  my $name  = shift;
  my $class = shift;
  my $time  = shift;

  return {
    name    => $name,
    class   => $class,
    'time'  => $time,
    failure => [],
    skipped => [],
  };
}

#
# Function: gen_failure
#
# Arg 1: $type     The type of the assert
# Arg 2: $message  The message specified in the assert
# Arg 3: $content  Usually the traceback
#
# This function populates and returns a hashref that represents a JUnit
# <failure></failure> XML block.  It can also be used to generate a JUnit
# <skipped></skipped> XML block which uses the same fields.
#
sub gen_failure {
  my $type    = shift;
  my $message = shift;
  my $content = shift;

  # MySQL test output sometimes contains bell (^G) characters, which
  # XML chokes on, even inside of CDATA blocks.
  $content =~ s/\007//g;

  return {
    type    => $type,
    message => $message,
    content => sprintf ("<![CDATA[%s]]>", $content),
  };
}
