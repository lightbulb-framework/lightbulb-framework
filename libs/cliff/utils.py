# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ctypes
import os
import struct
import sys

# Each edit operation is assigned different cost, such as:
#  'w' means swap operation, the cost is 0;
#  's' means substitution operation, the cost is 2;
#  'a' means insertion operation, the cost is 1;
#  'd' means deletion operation, the cost is 3;
# The smaller cost results in the better similarity.
COST = {'w': 0, 's': 2, 'a': 1, 'd': 3}


def damerau_levenshtein(s1, s2, cost):
    """Calculates the Damerau-Levenshtein distance between two strings.

    The Levenshtein distance says the minimum number of single-character edits
    (i.e. insertions, deletions, swap or substitution) required to change one
    string to the other.
    The idea is to reserve a matrix to hold the Levenshtein distances between
    all prefixes of the first string and all prefixes of the second, then we
    can compute the values in the matrix in a dynamic programming fashion. To
    avoid a large space complexity, only the last three rows in the matrix is
    needed.(row2 holds the current row, row1 holds the previous row, and row0
    the row before that.)

    More details:
        https://en.wikipedia.org/wiki/Levenshtein_distance
        https://github.com/git/git/commit/8af84dadb142f7321ff0ce8690385e99da8ede2f
    """

    if s1 == s2:
        return 0

    len1 = len(s1)
    len2 = len(s2)

    if len1 == 0:
        return len2 * cost['a']
    if len2 == 0:
        return len1 * cost['d']

    row1 = [i * cost['a'] for i in range(len2 + 1)]
    row2 = row1[:]
    row0 = row1[:]

    for i in range(len1):
        row2[0] = (i + 1) * cost['d']

        for j in range(len2):

            # substitution
            sub_cost = row1[j] + (s1[i] != s2[j]) * cost['s']

            # insertion
            ins_cost = row2[j] + cost['a']

            # deletion
            del_cost = row1[j + 1] + cost['d']

            # swap
            swp_condition = ((i > 0) and
                             (j > 0) and
                             (s1[i - 1] == s2[j]) and
                             (s1[i] == s2[j - 1])
                             )

            # min cost
            if swp_condition:
                swp_cost = row0[j - 1] + cost['w']
                p_cost = min(sub_cost, ins_cost, del_cost, swp_cost)
            else:
                p_cost = min(sub_cost, ins_cost, del_cost)

            row2[j + 1] = p_cost

        row0, row1, row2 = row1, row2, row0

    return row1[-1]


def terminal_width(stdout):
    if hasattr(os, 'get_terminal_size'):
        # python 3.3 onwards has built-in support for getting terminal size
        try:
            return os.get_terminal_size().columns
        except OSError:
            return None

    if sys.platform == 'win32':
        return _get_terminal_width_windows(stdout)
    else:
        return _get_terminal_width_ioctl(stdout)


def _get_terminal_width_windows(stdout):
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    std_to_win_handle = {
        sys.stdin: STD_INPUT_HANDLE,
        sys.stdout: STD_OUTPUT_HANDLE,
        sys.stderr: STD_ERROR_HANDLE}

    std_handle = std_to_win_handle.get(stdout)
    if not std_handle:
        return None

    handle = ctypes.windll.kernel32.GetStdHandle(std_handle)
    csbi = ctypes.create_string_buffer(22)

    res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, csbi)
    if res:
        (size_x, size_y, cur_pos_x, cur_pos_y, attr,
         left, top, right, bottom, max_size_x, max_size_y) = struct.unpack(
            "hhhhHhhhhhh", csbi.raw)
        return size_x


def _get_terminal_width_ioctl(stdout):
    from fcntl import ioctl
    import termios

    try:
        # winsize structure has 4 unsigned short fields
        winsize = b'\0' * struct.calcsize('hhhh')
        try:
            winsize = ioctl(stdout, termios.TIOCGWINSZ, winsize)
        except IOError:
            return None
        except TypeError:
            # this is raised in unit tests as stdout is sometimes a StringIO
            return None
        winsize = struct.unpack('hhhh', winsize)
        columns = winsize[1]
        if not columns:
            return None
        return columns
    except IOError:
        return None
