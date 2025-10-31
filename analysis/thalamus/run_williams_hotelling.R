library(bcdstats)
# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)

# Parse arguments
p1 <- as.numeric(args[1])
p2 <- as.numeric(args[2])
p12 <- as.numeric(args[3])
nobs <- as.numeric(args[4])

# Run the Williams-Hotelling test
result <- test2r.t2(p1, p2, p12, nobs)

# Output the p-value (this will be captured by Python)
cat(result$p_value)
