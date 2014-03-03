from pygments.style import Style
from pygments.token import *


class KoreanStyle(Style):

    background_color = '#eeeeee'
    default_style = ''

    styles = {
        Keyword:             '#985eaa', # class: 'k'
        Operator:            '#9e7da2', # class: 'o'
        Punctuation:         '#000000', # class: 'p'
        Name:                '#000000', # class: 'n'
        Name.Variable:       '#6d6b85', # class: 'nv'
        Number:              '#a56453', # class: 'm'
        String:              '#a56453', # class: 's'
        Generic.Output:      '#6c7086', # class: 'go'
        Generic.Prompt:      '#bdafa0', # class: 'gp'
    }


class TrueSkillStyle(Style):

    background_color = 'transparent'
    default_style = ''

    styles = {
        Comment:             '#aa9977',      # class: 'c'
        Comment.Single:      'italic',       # class: 'c1'
        Keyword:             '#b78e35',      # class: 'k'
        Keyword.Constant:    '#78c3c0',      # class: 'kc'
        Keyword.Declaration: '#ce6049',      # class: 'kd'
        Operator:            '#9e9a5f',      # class: 'o'
        Punctuation:         '#c2d76f',      # class: 'p'
        Name:                '#c8d841',      # class: 'n'
        Name.Attribute:      '#ce6049',      # class: 'na'
        Name.Builtin:        '#78c3c0',      # class: 'nb'
        Name.Tag:            'bold #f1ebc9', # class: 'nt'
        Number:              '#d37c59',      # class: 'm'
        String:              '#8db269',      # class: 's'
        String.Escape:       '#9e7da2',      # class: 'se'
        Generic.Output:      '#7f9574',      # class: 'go'
        Generic.Prompt:      '#569a81',      # class: 'gp'
    }


class HangulizeStyle(Style):

    background_color = '#333333'
    default_style = ''

    styles = {
        Comment:             '#aa9977',      # class: 'c'
        Comment.Single:      'italic',       # class: 'c1'
        Keyword:             '#faec8d',      # class: 'k'
        Keyword.Constant:    '#78c3c0',      # class: 'kc'
        Keyword.Declaration: '#ce6049',      # class: 'kd'
        Operator:            '#9e7da2',      # class: 'o'
        Punctuation:         '#999',         # class: 'p'
        Name:                '#ccc',         # class: 'n'
        Name.Attribute:      '#ce6049',      # class: 'na'
        Name.Builtin:        '#78c3c0',      # class: 'nb'
        Name.Tag:            'bold #6d7e9c', # class: 'nt'
        Number:              '#ce6049',      # class: 'm'
        String:              '#8db269',      # class: 's'
        String.Escape:       '#9e7da2',      # class: 'se'
        Generic.Output:      'bold #568',    # class: 'go'
        Generic.Prompt:      '#78c3c0',      # class: 'gp'
    }


class jDoctestStyle(Style):

    background_color = '#fafafa'
    default_style = ''

    styles = {
        Comment:             '#556677',      # class: 'c'
        Comment.Single:      'italic #a97',  # class: 'c1'
        Keyword:             '#992255',      # class: 'k'
        Keyword.Constant:    '#4455aa',      # class: 'kc'
        Keyword.Declaration: '#aa6611',      # class: 'kd'
        Operator:            '#666666',      # class: 'o'
        Punctuation:         '#333333',      # class: 'p'
        Name:                '#000000',      # class: 'n'
        Name.Attribute:      '#bb5588',      # class: 'na'
        Name.Builtin:        '#444422',      # class: 'nb'
        Name.Tag:            'bold #4455aa', # class: 'nt'
        Number:              '#bb6699',      # class: 'm'
        String:              '#669900',      # class: 's'
        Generic.Output:      'bold #556688', # class: 'go'
        Generic.Prompt:      '#887766',      # class: 'gp'
    }
