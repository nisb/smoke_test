#!/bin/bash
work_dir=$(dirname "$0")
script_path=$work_dir/sample_test.sikuli
/Applications/SikuliX/runsikulix -r "$script_path" --args -p "$work_dir/" -u