import datetime
import progressBar
import sys

class XmosTestException(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg
    
class XmosTest(object):
    
    TEST_FAIL=0
    TEST_PASS=1
    character_bank="1234567890-=qwetyuiop[]asdfghjkl;'#\\zxcvbnm,./ !\"$%^&*()_+QWERTYUIOP{}ASDFGHJKL:@~|ZXCVBNM<>?"
    
    test_state = None
    test_message = ""
    
    pb_enabled = 0
    log_file = None
    
    lf = sys.stdout
    
    def __init__(self, prog_bar=0, log_file=None):
        self.pb_enabled = prog_bar
        self.log_file = log_file
        
        if log_file is not None:
            lf = open(log_file, 'a')
    
    def setup_prog_bar(self, minValue = 0, maxValue = 10, totalWidth=12):
        if self.pb_enabled:
            self.pb_max_val = maxValue
            self.pb_min_val = minValue
            self.pb = progressBar.progressBar(minValue, maxValue , totalWidth)
        
    def update_prog_bar(self, value):
        if self.pb_enabled:
            self.pb.updateAmount(value)
            update_cond = int(self.pb_max_val/20)
            if update_cond == 0:
                update_cond = 1
            if ((value % update_cond == 0)):
                self.lf.write("\t"+str(self.pb)+"\r")
                self.lf.flush()
    
    def pb_print_start_test_info(self, test_name, target, message=None):
        """Print initial test message if utilising progress bar"""
        if self.pb_enabled:
            now = datetime.datetime.now()
            print >>self.lf, "["+now.strftime("%d-%m-%Y %H:%M")+"] Test: ",
            print >>self.lf, test_name,
            print >>self.lf, " Target: "+target
            if message is not None:
                print >>self.lf, "\tMessage: "+message

    def print_test_info(self, test_name, status, target=None, message=None):
        """Print standard end of test information"""
        now = datetime.datetime.now()
        
        print "["+now.strftime("%d-%m-%Y %H:%M")+"] Test: ",
        
        if status == self.TEST_FAIL:
            print >>self.lf, test_name,
            if target is not None:
                print >>self.lf, " Target: "+target,
            print >>self.lf, " Result: FAIL"
            if message is not None:
                print >>self.lf, "\tMessage: "+message
        if status == self.TEST_PASS:
            print >>self.lf, test_name,
            if target is not None:
                print >>self.lf, " Target: "+target,
            print >>self.lf, " Result: PASS"
            if message is not None:
                print >>self.lf, "\tMessage: "+message

    def print_to_log(self, test_name, message):
        if (self.log_file is not None):
            print >>self.lf, "["+now.strftime("%d-%m-%Y %H:%M")+"] Test: ",
            print >>self.lf, test_name,
            print >>self.lf, " Message: "+message
    
    def test_cleanup(self):
        if self.lf is not sys.stdout:
            self.lf.close()
    
    def test_finish_condition(self, test_duration_unit, test_duration, init=0):
        """Calculate if test should finish based on cycles or time - returns whether the loop should continue or not"""
        test_duration = int(test_duration)
        if (init):
            self.cycle_count = 0
            self.start_time = datetime.datetime.now()
            if (test_duration_unit =='minutes'):
                pbMax = test_duration * 60
            elif (test_duration_unit =='hours'):
                pbMax = test_duration * 60 * 60
            elif (test_duration_unit =='days'):
                pbMax = test_duration * 60 * 60 * 24
            else:
                pbMax = test_duration
            self.setup_prog_bar(0, pbMax, 20)
            
        test_condition = 1
        if (test_duration_unit =='cycles'):
                if (self.cycle_count < test_duration):
                    test_condition = 1
                else:
                    test_condition = 0
                self.cycle_count += 1
                self.update_prog_bar(self.cycle_count)
        elif (test_duration_unit =='seconds' or test_duration_unit =='minutes' or test_duration_unit =='hours' or test_duration_unit =='days'):
                update_div = 1
                current_time = datetime.datetime.now()
                delta = current_time - self.start_time
                
                if (test_duration_unit =='minutes'):
                    test_duration_unit = 'seconds'
                    test_duration = test_duration*60
                    update_div = 60
                    
                if (test_duration_unit =='hours'): 
                    test_duration_unit = 'seconds'
                    test_duration = test_duration*60*60
                    update_div = 60*60
                    
                if (getattr(delta, test_duration_unit) < test_duration):
                    test_condition = 1
                else:
                    test_condition = 0
                self.update_prog_bar(delta.seconds+(delta.days*24*60*60))
        else:
            raise XmosTestException("Invalid test duration unit - needs to be {cycles|seconds|minutes|hours|days} not "+str(test_duration_unit))
        
        return test_condition