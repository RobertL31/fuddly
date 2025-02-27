
import fuddly.tools.plotty.Formula as Formula
import fuddly.tools.plotty.cli.parse.formula as parse_formula
import fuddly.tools.plotty.cli.parse.range as parse_range

import unittest
import ddt


@ddt.ddt
class PlottyTest(unittest.TestCase):

#region Formula

    @ddt.data(
        {'formula': "a ~ b"},
        {'formula': "super_y_variable ~ extraordinary_x_variable"},
    )
    @ddt.unpack
    def test_should_return_parts_when_given_valid_formula(self, formula):
        result = parse_formula.parse_formula(formula)

        self.assertIsNotNone(result)


    @ddt.data(
        {'formula': "a = b"},
        {'formula': "f(a) = b"},
        {'formula': "exp((a + b) / c) cos(a + sin(b))"},
        {'formula': "a ~ b ~ c"},
    )
    @ddt.unpack
    def test_should_return_false_when_given_invalid_formula(self, formula):
        result = parse_formula.parse_formula(formula)

        self.assertIsNone(result)

    
#endregion
    
#region Range

    @ddt.data(
        {'range': ""},
        {'range': "not..a_range"},
        {'range': "definitely..not..a_range"},
        {'range': "10..1"},
        {'range': "100..1i0"},
        {'range': "10.."},
        {'range': "..10"},
    )
    @ddt.unpack
    def test_should_output_none_on_invalid_ranges(self, range):
        result = parse_range.parse_int_range(range)

        self.assertIsNone(result)


    @ddt.data(
        {'range': "1..4", 'expected_set': set(range(1, 4))},
        {'range': "0..1", 'expected_set': set(range(0, 1))},
        {'range': "547..960", 'expected_set': set(range(547,960))},
    )
    @ddt.unpack
    def test_should_retrieve_all_integers_given_well_formed_range(self, range, expected_set):
        result = parse_range.parse_int_range(range)
        print(result)
        self.assertIsNotNone(result)

        self.assertSetEqual(set(result), expected_set)


    @ddt.data(
        {'range_union': "1..4", 'expected_set': set([range(1, 4)])},
        {'range_union': "0..5, 5..10", 'expected_set': set([range(0, 5), range(5, 10)])},
        {'range_union': "0..120, 100..120", 'expected_set': set([range(0,120), range(100, 120)])},
        {
            'range_union': "0..120, 130..140, 150..200", 
            'expected_set': set([range(0, 120), range(130, 140), range(150, 200)])
        },
    )
    @ddt.unpack
    def test_should_find_all_ranges_of_ranges_union(self, range_union, expected_set):
        result = parse_range.parse_int_range_union(range_union)

        self.assertSetEqual(set(result), expected_set)

#endregion


    def dummy_test():
        pass
