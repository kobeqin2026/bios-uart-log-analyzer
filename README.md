# BIOS UART Log Analyzer

A Python script for analyzing BIOS UART logs to detect errors, extract hardware initialization information, and analyze boot timing during system bring-up.

## 📦 Versions

- **v0.2** (Latest): Enhanced fail keyword detection with dedicated output section
- **v0.1**: Initial release with basic BIOS log analysis features

[View all releases](https://github.com/kobeqin2026/bios-uart-log-analyzer/releases)

## Features

- 🔍 **Error Detection**: Automatically identifies common BIOS error patterns (error, fail, timeout, invalid, etc.)
- 🔧 **Hardware Information Extraction**: Extracts initialization info for CPU, Memory, PCIe, SATA, USB, Network
- ⏱️ **Boot Timing Analysis**: Supports multiple timestamp formats and calculates total boot time
- 📊 **Statistical Summary**: Provides line counts, keyword frequencies, and duplicate detection
- 🎯 **Bring-up Focused**: Specifically designed for GPU and hardware bring-up debugging
- 🚨 **Fail Keyword Highlighting**: Dedicated section showing all lines containing "fail" keyword with line numbers

## Installation

```bash
# Latest version
git clone https://github.com/kobeqin2026/bios-uart-log-analyzer.git
cd bios-uart-log-analyzer

# Specific version
git clone --branch v0.2 https://github.com/kobeqin2026/bios-uart-log-analyzer.git
cd bios-uart-log-analyzer
```

## Usage

### Basic Usage
```bash
python analyze_bios_uart_log.py your_bios_log.txt
```

### Advanced Usage
```bash
# Save detailed results as JSON
python analyze_bios_uart_log.py your_bios_log.txt --output results.json

# Verbose output with detailed analysis
python analyze_bios_uart_log.py your_bios_log.txt --verbose
```

## Output Example

The script provides comprehensive analysis including:
- **Summary statistics** (total lines, unique lines, empty lines)
- **Error detection** with line numbers and context
- **Hardware initialization** categorized by component type
- **Boot timing analysis** (if timestamps are present in logs)
- **Fail keyword detection** - dedicated section showing all "fail" occurrences with line numbers

### Sample Fail Detection Output
```
🔍 FAIL KEYWORD DETECTION (3)
------------------------------
Line 127: PCIe initialization failed - timeout
Line 234: Memory test fail on DIMM_A1  
Line 456: USB controller fail to initialize
```

## Use Cases

- **GPU Bring-up**: Quickly identify BIOS initialization issues during GPU bring-up
- **System Debugging**: Pinpoint hardware detection failures or timeouts
- **Performance Analysis**: Measure boot sequence timing for optimization
- **Log Comparison**: Compare different BIOS versions or configurations

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## License

MIT License