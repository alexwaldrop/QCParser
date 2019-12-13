from QCModules.BaseModule import QCParseException
from BaseParser import BaseParser

class Trimmomatic(BaseParser):

    DESCRIPTION     = "Parse Trimmomatic stderr log."
    INPUT_FILE_DESC = "Trimmomatic stderr log"

    def __init__(self, sys_args):
        super(Trimmomatic, self).__init__(sys_args)

    def parse_input(self):
        # open input file
        is_paired   = True
        header_seen = False
        with open(self.input_file, "r") as fh:
            for line in fh:
                # find line with number of reads input and surviving trimming
                if not header_seen and "TrimmomaticSE" in line:
                    is_paired   = False
                    header_seen = True
                elif not header_seen and "TrimmomaticPE" in line:
                    header_seen = True
                elif "Surviving" in line:
                    if is_paired:
                        # paired-end output
                        input_reads = int(line.strip().split()[3]) * 2
                        #trimmed_reads = int(line.strip().split()[6]) * 2
                        r1_trimmed_unpaired = int(line.strip().split()[11])
                        r2_trimmed_unpaired = int(line.strip().split()[16])
                        trimmed_paired = int(line.strip().split()[6]) * 2
                        trimmed_reads = trimmed_paired + r1_trimmed_unpaired + r2_trimmed_unpaired
                    else:
                        # single-end output
                        input_reads = int(line.strip().split()[2])
                        trimmed_reads = int(line.strip().split()[4])
                    self.add_entry("Input_Reads", input_reads)
                    self.add_entry("Trimmed_Reads", trimmed_reads)
                    if is_paired:
                        self.add_entry("Trimmed_Paired", trimmed_paired)
                        self.add_entry("Trimmed_F_only", r1_trimmed_unpaired)
                        self.add_entry("Trimmed_R_only", r2_trimmed_unpaired)
                    break

            # Raise exception if header line never seen
            if not header_seen:
                raise QCParseException("Input file is not output from trimmomatic!")

    def define_required_colnames(self):
        return ["Input_Reads", "Trimmed_Reads"]