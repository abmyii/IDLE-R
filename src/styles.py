#
#  styles.py
#
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Whitespace


class PythonStyle(Style):
    """
    A colorful style, inspired by the IDLE style.
    """

    default_style = ""

    styles = {
        Whitespace:                 '#ffffff', # Whitespace (html)

        Comment:                    '#dd0000', # Comments
        Comment.Preproc:            '#dd0000', # Comments (?)
        Comment.Special:            '#dd0000', # Comments (?)

        Keyword:                    '#ff7700', # Keywords
        Keyword.Type:               '#ff7700', # Keywords
        Keyword.Constant:           '#800080', # True/False

        Operator.Word:              '#ff7700', # in, and, or (and such)

        Name.Builtin:               '#800080', # all, abs (and such)
        Name.Builtin.Pseudo:        '#000000', # self, True, False
        Name.Function:              '#0000aa', # def <name.function>
        Name.Class:                 '#0000aa', # class <name.class>
        Name.Namespace:             '#000000', # import <...> or from <...>
        Name.Variable:              '#aa0000', # ?
        Name.Constant:              '#aa0000', # ?
        Name.Entity:                'bold #800', # ?
        Name.Attribute:             '#1e90ff', # ?
        Name.Tag:                   'bold #1e90ff', # ?
        Name.Decorator:             '#800080', # Decorator

        String:                     '#008000', # String
        String.Symbol:              '#008000', # String
        String.Regex:               '#008000', # String

        Number:                     '#007000',  # Numbers

        Generic.Heading:            'bold #000080', # ?
        Generic.Subheading:         'bold #800080', # ?
        Generic.Deleted:            '#aa0000', # ?
        Generic.Inserted:           '#00aa00', # ?
        Generic.Error:              '#aa0000', # ?
        Generic.Emph:               'italic', # ?
        Generic.Strong:             'bold', # ?
        Generic.Prompt:             '#555555', # ?
        Generic.Output:             '#888888', # ?
        Generic.Traceback:          '#aa0000', # ?

        Error:                      '#F00 bg:#FAA' # Errors
    }
