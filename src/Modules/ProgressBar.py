__all__ = ['tqdm', 'trange']

import sys
import time
import GetTerminalSize

NumberOfFinishedResults = 0

def format_interval(t):
    mins, s = divmod(int(t), 60)
    h, m = divmod(mins, 60)
    if h:
        return '%d:%02d:%02d' % (h, m, s)
    else:
        return '%02d:%02d' % (m, s)


def format_meter_second(n, total, elapsed):
    # n - number of finished iterations
    # total - total number of iterations, or None
    # elapsed - number of seconds passed since start
    if n > total:
        total = None
    
    elapsed_str = format_interval(elapsed)
    rate = '%5.2f' % (n / elapsed) if elapsed else '?'
    
    if total:
        frac = float(n) / total
        percentage = '%3d%%' % (frac * 100)
        left_str = format_interval(elapsed / n * (total-n)) if n else '?'

        RemainingLength=max(len(' %d/%d %s [elapsed: %s left: %s, %s iters/sec]' % (
             n, total, percentage, elapsed_str, left_str, rate)),
                        len('%d [elapsed: %s, %s iters/sec]' % (n, elapsed_str, rate)))

        N_BARS = GetTerminalSize.get_terminal_size()[0]-RemainingLength-3
        bar_length = int(frac*N_BARS)
        bar = '#'*bar_length + '-'*(N_BARS-bar_length) 
        
        return '|%s| %d/%d %s [elapsed: %s left: %s, %s iters/sec]' % (
            bar, n, total, percentage, elapsed_str, left_str, rate)
    
    else:
        return '%d [elapsed: %s, %s iters/sec]' % (n, elapsed_str, rate)

def format_meter_minute(n, total, elapsed):
    # n - number of finished iterations
    # total - total number of iterations, or None
    # elapsed - number of minutes passed since start
    if n > total:
        total = None
    
    elapsed_str = format_interval(elapsed*60)
    rate = '%5.2f' % (n / elapsed) if elapsed else '?'
    
    

    if total:
        frac = float(n) / total
        percentage = '%3d%%' % (frac * 100)
        left_str = format_interval(elapsed*60 / n * (total-n)) if n else '?'

        RemainingLength=max(len(' %d/%d %s [elapsed: %s left: %s, %s iters/min]' % (
             n, total, percentage, elapsed_str, left_str, rate)),
                        len('%d [elapsed: %s, %s iters/min]' % (n, elapsed_str, rate)))

        N_BARS = GetTerminalSize.get_terminal_size()[0]-RemainingLength-3
        bar_length = int(frac*N_BARS)
        bar = '#'*bar_length + '-'*(N_BARS-bar_length) 
        
        return '|%s| %d/%d %s [elapsed: %s left: %s, %s iters/min]' % (
            bar, n, total, percentage, elapsed_str, left_str, rate)
    
    else:
        return '%d [elapsed: %s, %s iters/min]' % (n, elapsed_str, rate)

def format_meter_hour(n, total, elapsed):
    # n - number of finished iterations
    # total - total number of iterations, or None
    # elapsed - number of minutes passed since start
    if n > total:
        total = None
    
    elapsed_str = format_interval(elapsed*3600)
    rate = '%5.2f' % (n / elapsed) if elapsed else '?'
    
    

    if total:
        frac = float(n) / total
        percentage = '%3d%%' % (frac * 100)
        left_str = format_interval(elapsed*3600 / n * (total-n)) if n else '?'

        RemainingLength=max(len(' %d/%d %s [elapsed: %s left: %s, %s iters/hour]' % (
             n, total, percentage, elapsed_str, left_str, rate)),
                        len('%d [elapsed: %s, %s iters/hour]' % (n, elapsed_str, rate)))

        N_BARS = GetTerminalSize.get_terminal_size()[0]-RemainingLength-3
        bar_length = int(frac*N_BARS)
        bar = '#'*bar_length + '-'*(N_BARS-bar_length) 
        
        return '|%s| %d/%d %s [elapsed: %s left: %s, %s iters/hour]' % (
            bar, n, total, percentage, elapsed_str, left_str, rate)
    
    else:
        return '%d [elapsed: %s, %s iters/hour]' % (n, elapsed_str, rate)


class StatusPrinter(object):
    def __init__(self, file):
        self.file = file
        self.last_printed_len = 0
    
    def print_status(self, s):
        self.file.write('\r'+s+' '*max(self.last_printed_len-len(s), 0))
        self.file.flush()
        self.last_printed_len = len(s)


def tqdm(iterable, desc='', total=None, leave=False, file=sys.stderr,
         mininterval=0.1, miniters=1, type="minute"):
    """
    Get an iterable object, and return an iterator which acts exactly like the
    iterable, but prints a progress meter and updates it every time a value is
    requested.
    'desc' can contain a short string, describing the progress, that is added
    in the beginning of the line.
    'total' can give the number of expected iterations. If not given,
    len(iterable) is used if it is defined.
    'file' can be a file-like object to output the progress message to.
    If leave is False, tqdm deletes its traces from screen after it has
    finished iterating over all elements.
    If less than mininterval seconds or miniters iterations have passed since
    the last progress meter update, it is not updated again.
    """

    if type!="second" and type!="hour":
        type="minute"
    if total is None:
        try:
            total = len(iterable)
        except TypeError:
            total = None
    
    prefix = desc+': ' if desc else ''
    
    sp = StatusPrinter(file)
    if type=="minute":
        sp.print_status(prefix + format_meter_minute(0, total, 0))
    elif type=="second":
        sp.print_status(prefix + format_meter_second(0, total, 0))
    else:
        sp.print_status(prefix + format_meter_hour(0, total, 0))
    
    start_t = last_print_t = time.time()
    last_print_n = 0
    n = 0
    for obj in iterable:
        yield obj
        # Now the object was created and processed, so we can print the meter.
        n += 1
        if n - last_print_n >= miniters:
            # We check the counter first, to reduce the overhead of time.time()
            cur_t = time.time()
            if cur_t - last_print_t >= mininterval:
                if type=="minute":
                    sp.print_status(prefix + format_meter_minute(n, total, (cur_t-start_t)/60))
                elif type=="second":
                    sp.print_status(prefix + format_meter_second(n, total, (cur_t-start_t)))
                else:
                    sp.print_status(prefix + format_meter_hour(n, total, (cur_t-start_t)/3600))
                last_print_n = n
                last_print_t = cur_t
    
    if not leave:
        sp.print_status('')
        sys.stdout.write('\r')
    else:
        if last_print_n < n:
            cur_t = time.time()
            if type=="minute":
                sp.print_status(prefix + format_meter_minute(n, total, (cur_t-start_t)/60))
            elif type=="second":
                sp.print_status(prefix + format_meter_second(n, total, (cur_t-start_t)))
            else:
                sp.print_status(prefix + format_meter_hour(n, total, (cur_t-start_t)/3600))
        file.write('\n')


def trange(*args, **kwargs):
    """A shortcut for writing tqdm(range()) on py3 or tqdm(xrange()) on py2"""
    try:
        f = xrange
    except NameError:
        f = range
    
    return tqdm(f(*args), **kwargs)