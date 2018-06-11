import os.path, subprocess
from subprocess import check_output, call

svg_file = "greeter_2018-06-06_1528305118.svg"
old_svg_sum_file = "/tmp/greeter-last-svg-sum.txt"
new_svg_sum = check_output(["sum", svg_file])
new_sum = new_svg_sum.split(" ")
#print(svg_sum[0])

if os.path.isfile(old_svg_sum_file):
    old_svg_sum = check_output(["cat", old_svg_sum_file])
    old_sum = old_svg_sum.split("\n")
    print('old svg sum file found containing: %s'%old_sum[0])

    if new_sum[0] == old_sum[0]:
        print('No changes detected between last run. Exiting')
        exit()
    else:
        # we detected changes so update the old_svg_sum
        print('old sum is different than new sum %s|%s'%(old_sum[0],new_sum[0]))
        with open(old_svg_sum_file, 'w') as f:
            f.write(new_sum[0])
        f.close
        print('updated old svg sum file')
else:
    # did not find the old svg sum file, so we will create it and continue
    print('Did not find old svg sum file so we will create a new one which contains [%s]'%new_sum[0])
    with open(old_svg_sum_file, 'w') as f:
        f.write(new_sum[0])
    f.close

