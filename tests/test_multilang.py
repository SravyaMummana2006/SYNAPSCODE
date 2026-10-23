"""
Unit tests for Multi-Language Tree-Sitter Detector (C++ and Python).
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from multilang.tree_sitter_detector import TreeSitterDetector

CPP_CODE_ORIG = """
#include <vector>

int binary_search(const std::vector<int>& arr, int target) {
    int left = 0;
    int right = arr.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}
"""

CPP_CODE_RENAME = """
#include <vector>

int binary_search(const std::vector<int>& numbers, int key) {
    int start_pos = 0;
    int end_pos = numbers.size() - 1;
    while (start_pos <= end_pos) {
        int center = start_pos + (end_pos - start_pos) / 2;
        if (numbers[center] == key) {
            return center;
        } else if (numbers[center] < key) {
            start_pos = center + 1;
        } else {
            end_pos = center - 1;
        }
    }
    return -1;
}
"""

CPP_CODE_INDEPENDENT = """
#include <vector>

int binary_search(const std::vector<int>& arr, int target) {
    // Recursive independent implementation
    auto helper = [&](auto& self, int lo, int hi) -> int {
        if (lo > hi) return -1;
        int m = (lo + hi) / 2;
        if (arr[m] == target) return m;
        if (arr[m] > target) return self(self, lo, m - 1);
        return self(self, m + 1, hi);
    };
    return helper(helper, 0, (int)arr.size() - 1);
}
"""

class TestTreeSitterMultiLang(unittest.TestCase):
    def setUp(self):
        self.detector_cpp = TreeSitterDetector(lang="cpp", k=1, w=2)
        self.detector_py = TreeSitterDetector(lang="python", k=1, w=2)

    def test_cpp_rename_plagiarism_detection(self):
        """C++ renamed code should show very high structural similarity."""
        res = self.detector_cpp.compare_codes(CPP_CODE_ORIG, CPP_CODE_RENAME)
        # Because Tree-Sitter abstracts variable names, similarity should be >= 80%
        self.assertGreaterEqual(res.jaccard, 0.80)
        self.assertGreater(res.execution_time_sec, 0.0)

    def test_cpp_independent_solution_discrimination(self):
        """C++ independent recursive solution should have lower similarity than renamed."""
        res_indep = self.detector_cpp.compare_codes(CPP_CODE_ORIG, CPP_CODE_INDEPENDENT)
        res_plag = self.detector_cpp.compare_codes(CPP_CODE_ORIG, CPP_CODE_RENAME)
        self.assertGreater(res_plag.jaccard, res_indep.jaccard)

    def test_python_tree_sitter_support(self):
        """Verify Python parsing also functions seamlessly through Tree-Sitter."""
        py1 = "def add(x, y): return x + y"
        py2 = "def add(a, b): return b + a"
        res = self.detector_py.compare_codes(py1, py2)
        self.assertEqual(res.jaccard, 1.0)

if __name__ == "__main__":
    unittest.main()
