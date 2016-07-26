"""
Config file for The Powder Toy's website <http://powdertoy.co.uk>
Contains the message we post before we lock a thread, group ID, whitelist, etc.
"""
daysUntilLock = 182
daysUntilDelete = 200
lockmsg = ''.join([
    '<p>Hey there!</p>',
    '<p>We\'re automatically closing this thread since the original poster ',
    '(or another commenter) hasn\'t posted on this thread '
    'since {0} days ago. '.format(str(daysUntilLock)),
    'We therefore assume that the user has lost interest or the topic ',
    'is now defunct. ',
    'Closed threads that remain inactive for a long period may ',
    'get automatically deleted.</p>',
    '<p>Don\'t worry though; if this is in error, let us know in a private ',
    'message and ',
    'we\'ll be happy to reopen the thread.</p>',
    '<p>Thanks!</p>',
    '<p><small><i>(Please note that this is an automated comment.)',
    '</i></small></p>'
])
password = 'BrilliantMinds!',
username = 'BMNNation',
whitelist = ['1427', '2202', '2228']
groupID = '832'

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
