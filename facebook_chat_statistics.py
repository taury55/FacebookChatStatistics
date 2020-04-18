import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import warnings
from facebook_messenger_conversation import FacebookMessengerConversation

warnings.filterwarnings('ignore', module='matplotlib')


def main():
    """
    Fetches and prints statistics of a Facebook Messenger
    conversation. Also generates a PDF with plots of
    some of these statistics.
    """
    if len(sys.argv) == 2:
         path_to_conversation = str(sys.argv[1])
    else:
        print('Usage: python3 {} /Path/To/Conversation/'
        .format(sys.argv[0]))
        sys.exit()

    fb = FacebookMessengerConversation(path_to_conversation)
    nbr_of_top_emojis = 10

    participants = fb.get_participants()

    print(banner('Times'))
    start, end = fb.get_time_interval('str')
    print('Start: {}\nEnd: {}'.format(start, end))

    print(banner('Totals'))
    activity = fb.activity()
    for act_p in activity:
        print('Number of messages {}: {} ({} %)'.format(act_p,
                                                        activity[act_p][0],
                                                        activity[act_p][1]))
    nbr_days = fb.get_nbr_days()
    print('Number of days: {}'.format(nbr_days))
    print('Number of messages: {}'.format(fb.get_nbr_msg()))
    print('Number of words: {}'.format(fb.get_nbr_words()))

    print(banner('Averages'))
    print('Average length of messages: {} words'.format(fb.get_avg_len_msg()))
    print('Average messages per day: {}'.format(fb.get_avg_msg_day()))

    print(banner('Plots'))

    names = ''
    for p in participants:
        name = p.split(' ')
        names += '{}_{}_'.format(name[0], name[1])
    names = names[:-1]
    output_filename = path_to_conversation.split('/')
    filename = '{}_{}_{}.pdf'.format(str(output_filename[-2]), start[0:10].replace('-', ''),
                                     end[0:10].replace('-',''))

    # Generate PDF
    with PdfPages(filename) as pdf:
        # General info
        fig = plt.figure(dpi=160)
        ax = fig.add_subplot(1,1,1)
        table_data=[
            ["Start", start],
            ["End", end],
            ["Number of days", fb.get_nbr_days()],
            ["Number of messages", fb.get_nbr_msg()],
            ["Number of words", fb.get_nbr_words()],
            ["Average length of messages", str(fb.get_avg_len_msg()) + " words"],
            ["Average message per day", fb.get_avg_msg_day()]
        ]
        table = ax.table(cellText=table_data, loc='center')
        table.set_fontsize(14)
        table.scale(1,4)
        # Removing ticks and spines enables you to get the figure only with table
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
        for pos in ['right','top','bottom','left']:
            plt.gca().spines[pos].set_visible(False)
        pdf.savefig(pad_inches=0.05)
        plt.close()

        # Plot percentage
        fracs = [activity[act_p][0] for act_p in activity]
        theme = plt.get_cmap('hsv')

        fig1, ax1 = plt.subplots()
         
        ax1.set_prop_cycle("color", [theme(1. * i / len(fracs))
                                     for i in range(len(fracs))])

        _, _ = ax1.pie(fracs, startangle=90)
        plt.legend(loc='upper left',
                   bbox_to_anchor=(-0.15, 1.15),
                   labels=['%s, %i, %1.1f%%' % (l, s, s * 100 / fb.get_nbr_msg())
                       for l, s in zip(participants, fracs)],
                   prop={'size': 8})
        ax1.axis('equal')
        plt.title('Who texts the most?')
        pdf.savefig()
        plt.close()

        # Plot timeline
        timeline, nbr_times_day, nbr_times_weekday, nbr_times_hour = fb.timeline()
        months = nbr_days/30
        interval = int(round(months/12))
        fmt = mdates.DateFormatter('%Y-%m-%d')
        loc = mdates.MonthLocator(interval=interval)
        ax = plt.axes()
        ax.xaxis.set_major_formatter(fmt)
        plt.bar(timeline, nbr_times_day, align='center', width=8)
        plt.title('Timeline')
        plt.ylabel('Number of messages')
        ax.yaxis.grid(linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['left'].set_linewidth(0.5)
        fig = plt.figure(1)
        fig.autofmt_xdate()
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # Plot by hour
        hour = list(range(24))
        plt.bar(hour, nbr_times_hour, align='center', width=0.8)
        plt.title('Activity by Day')
        plt.xlabel('Hour of the day')
        plt.ylabel('Number of messages')
        ax = plt.axes()
        ax.yaxis.grid(linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['left'].set_linewidth(0.5)
        fig = plt.figure(1)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # Plot by weekday
        weekday_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                          'Friday', 'Saturday', 'Sunday']
        weekday_arr = np.arange(len(weekday_labels))
        plt.bar(weekday_arr, nbr_times_weekday, align='center', width=0.8)
        plt.xticks(weekday_arr, weekday_labels, rotation=30)
        plt.title('Activity by Week')
        plt.ylabel('Number of messages')
        ax = plt.axes()
        ax.yaxis.grid(linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['left'].set_linewidth(0.5)
        fig = plt.figure(1)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # Plot top emojies
        top_emojis, emoji_count_p = fb.top_emojis(nbr_of_top_emojis)
        x = np.arange(len(top_emojis))
        plt.bar(x, emoji_count_p[participants[0]], align='center', width=0.8)
        emoji_sum = emoji_count_p[participants[0]]
        for i in range(1, len(participants)):
            plt.bar(x, emoji_count_p[participants[i]],
                    align='center', width=0.8, bottom=emoji_sum)
            emoji_sum = [x + y for x, y in zip(emoji_sum, emoji_count_p[participants[i]])]
        plt.xticks(x, top_emojis)
        plt.title('Top 10 emojis')
        plt.ylabel('Number of times used')
        plt.legend(participants)
        ax = plt.axes()
        ax.yaxis.grid(linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['left'].set_linewidth(0.5)
        fig = plt.figure(1)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # PDF info
        d = pdf.infodict()
        d['Title'] = filename.replace('_', ' ')
        d['Author'] = 'Facebook Chat Statistics'
        d['Subject'] = 'Conversation statistics between {}'.format(
            names.replace('_', ' '))
        d['CreationDate'] = datetime.today()
        d['ModDate'] = datetime.today()

    print('Most messages in one day: {}'.format(max(nbr_times_day)))
    print('Top 10 emojis: {}'.format(top_emojis))
    print('PDF generated successfully!')


def banner(msg, ch='=', length=80):
    """Creates a banner with the message `msg`.

    Args:
        msg (str): Message of banner.
        ch (str): Banner character.
        length (int): Length of banner.

    Returns:
        str: Banner with message.

    """
    spaced_text = ' {} '.format(msg)
    banner = spaced_text.center(length, ch)
    return banner


if __name__ == '__main__':
    main()
