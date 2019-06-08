import numpy as np
import pandas as pd
from IPython.core.display import display
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import PIL


# ../input/train_ship_segmentations_v2.csv for Windows and Kaggle, ./input/train_ship_segmentations_v2.csv for MacOS
df_tmp = pd.read_csv("./input/train_ship_segmentations_v2.csv").dropna()
df_tmp = df_tmp.drop_duplicates("ImageId", keep='first')
df_tmp.to_csv("./tmp.csv", index_label=False, index=False)

df = pd.read_csv("./tmp.csv", index_col=0).dropna()

# turn rle example into a list of ints
rle = [int(i) for i in df['EncodedPixels']['55bd28f41.jpg'].split()]
# turn list of ints into a list of (`start`, `length`) `pairs`
pairs = list(zip(rle[0:-1:2], rle[1::2]))

start = pairs[0][0]
print(f"Original start position: {start}")

coordinate = (start % 768, start // 768)
print(f"Maps to this coordinate: {coordinate}")

back = 768 * coordinate[1] + coordinate[0]
print(f"And back: {back}")

pixels = [(pixel_position % 768, pixel_position // 768)
                            for start, length in pairs
                            for pixel_position in range(start, start + length)]


def rle_to_pixels(rle_code):
    '''
    Transforms a RLE code string into a list of pixels of a (768, 768) canvas
    '''
    rle_code = [int(i) for i in rle_code.split()]
    pixels = [(pixel_position % 768, pixel_position // 768)
                 for start, length in list(zip(rle_code[0:-1:2], rle_code[1::2]))
                 for pixel_position in range(start, start + length)]
    return pixels

# An image may have more than one row in the df,
# Meaning that the image has more than one ship present
# Here we merge those n-ships into the a continuos rle-code for the image....
df = df.groupby("ImageId")[['EncodedPixels']].agg(lambda rle_codes: ' '.join(rle_codes)).reset_index()


for i in range(2000):
    row_index = np.random.randint(len(df))  # take a random row from the df
    mask_pixels = rle_to_pixels(df.loc[row_index, 'EncodedPixels'])
    tuple_y, tuple_x = zip(*mask_pixels)
    table_x = list(tuple_x)
    table_y = list(tuple_y)
    x_min = min(table_x)
    y_min = min(table_y)
    x_max = max(table_x)
    y_max = max(table_y)
    with open("entry_data.txt", "a") as f:
        print(df.loc[row_index, 'ImageId'], x_min, y_min, x_max, y_max, "ship", sep=',',
              file=f)
    f.close()

    # NOTE: uncomment following part for checking if the Bounding Boxes are correctly selected

    # load_img = lambda filename: np.array(PIL.Image.open(f"./input/train_v2/{filename}"))
    # im = np.array(load_img(df.loc[row_index, 'ImageId']), dtype=np.uint8)
    # # Create figure and axes
    # fig, ax = plt.subplots(1)
    # # Display the image
    # ax.imshow(im)
    # # Create a Rectangle patch
    # rect = patches.Rectangle((x_min, y_min), x_max-x_min, y_max-y_min, linewidth=1, edgecolor='r', facecolor='none')
    # # Add the patch to the Axes
    # ax.add_patch(rect)
    # ax.set_title(df.loc[row_index, 'ImageId'])
    # plt.show()

print("Finished")
