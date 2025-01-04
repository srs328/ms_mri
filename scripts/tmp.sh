#!/bin/bash





default_app=bar

# while getopts ":a:b:c" opt; do
#     case $opt in
#         a)
#             if [ -z $OPTARG ]; then
#                 app=default_app
#             else
#                 app=$OPTARG
#             fi
#             echo "Using $app to open"
#             ;;
#     esac
# done

# subid=${@:$OPTIND:1}

# echo $subid

usage() {
    echo "Usage: $0 [-f <file>] [-v] [-h]"
    echo "  -f <file>  Specify the input file."
    echo "  -v         Enable verbose mode."
    echo "  -h         Display this help message."
    exit 0
}

script_args=()
while [ $OPTIND -le "$#" ]
do
    if getopts :a:b:c:h opt
    then
        case $opt in
            a)
                app=$OPTARG
                ;;
            h)
                usage ;;
        esac
    else
        script_args+=("${!OPTIND}")
        ((OPTIND++))
    fi
done

subid=${script_args[0]}

echo $subid