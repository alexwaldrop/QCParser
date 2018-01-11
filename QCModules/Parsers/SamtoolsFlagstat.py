import logging

from BaseParser import BaseParser
from QCModules.BaseModule import QCParseException

class SamtoolsFlagstat(BaseParser):

    DESCRIPTION     = "Parse Samtools flagstat output (v1.3 and later)"
    INPUT_FILE_DESC = "Samtools flagstat output"

    def __init__(self, sys_args):
        super(BaseParser, self).__init__(sys_args)

    def make_qc_report(self):
        # Parse samtools flagstat
        first_line = True
        with open(self.input_file, "r") as fh:
            for line in fh:
                if first_line:
                    # Check to make sure file actually samtools flagstat file
                    if "in total" not in line:
                        raise QCParseException("File provided is not output from samtools Flagstat")

                    # Get total reads in BAM file
                    tot_aligns = float(line.split()[0])
                    first_line = False

                elif "secondary" in line:
                    secondary_aligns = float(line.split()[0])

                elif "supplementary" in line:
                    supp_aligns = float(line.split()[0])

                elif "duplicates" in line:
                    # Get total duplicates
                    pcr_dups = float(line.split()[0])

                elif "mapped (" in line:
                    # Get number aligned reads
                    mapped_reads = float(line.split()[0])

                elif "paired in sequencing" in line:
                    # Get number, percent of properly paired reads
                    paired = float(line.split()[0])

                elif "properly paired" in line:
                    # Get number, percent of properly paired reads
                    prop_paired = float(line.split()[0])

                elif "singletons" in line:
                    # Get number, percent of singleton reads (mate doesn't map)
                    singletons = float(line.split()[0])

                elif "with mate mapped to a different chr" in line and "(mapQ" not in line:
                    # Get number, percent of reads where mates map to different chromosome
                    tot_mate_diff_chrom_lq = float(line.split()[0])

                elif "with mate mapped to a different chr" in line and "(mapQ" in line:
                    # Get number, percent of reads where mates map to different chromosome with high quality
                    tot_mate_diff_chrom_hq = float(line.split()[0])

            # Add basic samtools fields
            self.add_entry("Tot_aligns", tot_aligns)
            self.add_entry("Sec_aligns", secondary_aligns)
            self.add_entry("Supp_aligns", supp_aligns)
            self.add_entry("PCR_dups", pcr_dups)
            self.add_entry("Mapped_Reads", mapped_reads)
            self.add_entry("Proper_Paired", prop_paired)
            self.add_entry("Singletons", singletons)
            self.add_entry("Mate_Mapped_Diff_Chrom_LQ", tot_mate_diff_chrom_lq)
            self.add_entry("Mate_Mapped_Diff_Chrom_HQ", tot_mate_diff_chrom_hq)

            # Compute real mapping rates (number of actually good mappings / actual number of reads in bam)
            is_paired   = paired > 0
            total_reads = tot_aligns - secondary_aligns - supp_aligns
            if is_paired:
                logging.info("Paired in sequences detected for BAM: %s" % self.input_file)
                self.add_entry("Real_Map_Rate", (prop_paired/total_reads) * 100)
            else:
                logging.info("Single-end sequences detected for BAM: %s" % self.input_file)
                self.add_entry("Real_Map_Rate", (mapped_reads/total_reads) * 100)
