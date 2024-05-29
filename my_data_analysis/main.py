"""My data analysis for my undergraduate honors project"""
import pandas as pd
import numpy as np
import os

# Step 0: Place a participant's gaze_positions.csv and the csv for the AOI info into the folder with this file.

# Ask user for file names
print("\n***** Press Ctrl + C to exit this program at any time *****\n")
aoi_filename = input("\nInput AOI data file name for this participant\n"
                     "(generated by the Dynamic AOI Toolkit): ")
gaze_filename = input("\nInput gaze positions file name for this participant (from PupilLabs): ")
participant_identifier = input("\nInput a participant identifier"
                               "\n(a number or first initial is recommended): ")

print("\nPlease allow 3-10 minutes for the process to complete\n")

# Step 1: Read both csvs as pandas and convert to numpy dataframes.
df_gaze = pd.read_csv(gaze_filename)
df_aoi = pd.read_csv(aoi_filename)
gaze_np = df_gaze.to_numpy()
aoi_np = df_aoi.to_numpy()

# Step 2: Convert the gaze data's rows into frames by
# only using the measurement taken at the start of every frame.

# Get the first frame in the AOI csv.
first_frame = aoi_np[0][0]

# Remove duplicate frame values from the AOI numpy table (only the first frame value for a given frame will be taken).
new_aoi_np = aoi_np
offset = 0
current_frame_val = first_frame
for index, row in enumerate(aoi_np):

    next_row_index = index + 1
    if next_row_index < np.shape(aoi_np)[0]:
        next_row_value = aoi_np[next_row_index, 0]

        # Remove the row with the duplicated frame value
        if next_row_value == current_frame_val:
            new_aoi_np = np.delete(new_aoi_np, next_row_index - offset, 0)
            offset += 1
        current_frame_val = next_row_value
    else:
        break

print("Removed duplicate frame values from the AOI file")

if new_aoi_np is not None:
    aoi_np = new_aoi_np

# Do the same (remove duplicate frame values) for the gaze numpy table
current_row_value = gaze_np[0][1]
new_gaze_np = gaze_np
offset = 0

for index, row in enumerate(gaze_np):
    current_row_value = row[1]
    next_row_index = index + 1
    if next_row_index < np.shape(gaze_np)[0]:
        next_row_value = gaze_np[next_row_index, 1]

        if next_row_value == current_row_value:
            new_gaze_np = np.delete(new_gaze_np, next_row_index - offset, 0)
            offset += 1
    else:
        break

if new_gaze_np is not None:
    gaze_np = new_gaze_np

print("Removed duplicate frame values from the gaze positions file")

# Find all the "gaps" in aoi_np (places where the frame of row n+1 is not 1 greater than frame n).
# These represent parts of the video that do not have an AOI bounding box on them.
# NOTE: The "gaps" list contains tuples of the form (start of gap index, end of gap index)
gaps = []
for row_index, row in enumerate(aoi_np):
    if row_index + 1 < np.shape(aoi_np)[0]:
        current_frame_val = aoi_np[row_index][0]
        next_frame_val = aoi_np[row_index + 1][0]
        if next_frame_val - current_frame_val > 1:
            gaps.append((current_frame_val, next_frame_val))

# This value may have to be adjusted up or down depending on small fluctuations in the data.
offset = 2

# Delete rows from gaze_np that align with gaps in aoi_np.
new_gaze_np = gaze_np
for start_of_gap, end_of_gap in gaps:
    current_index = start_of_gap + 1
    while current_index < end_of_gap:
        if (current_frame_val - offset) < np.shape(new_gaze_np)[0]:
            new_gaze_np = np.delete(new_gaze_np, current_index - offset, 0)
        current_index += 1
        offset += 1

if new_gaze_np is not None:
    gaze_np = new_gaze_np

print("Removed values from the gaze file that do not have an associated AOI")

# Remove all the rows in gaze_np that are after the last row of aoi_np or before the first row of aoi_np
last_frame_value = aoi_np[-1, 0]
first_frame_value = aoi_np[0, 0]
new_gaze_np = gaze_np
offset = 0

for index, row in enumerate(gaze_np):
    current_frame_val = row[1]

    if current_frame_val > last_frame_value or current_frame_val < first_frame_value:
        new_gaze_np = np.delete(new_gaze_np, index - offset, 0)
        offset += 1

if new_gaze_np is not None:
    gaze_np = new_gaze_np

print("Removed excess values from the gaze positions data at the beginning and end of the file")

# Write the converted numpy tables to new csv files.
aoi_df = pd.DataFrame(data=aoi_np, columns=['Frame', 'Object ID', 'category', 'x1', 'x2', 'y1', 'y2', 'type'])
gaze_df = pd.DataFrame(data=gaze_np, columns=['gaze_timestamp', 'world_index', 'confidence', 'norm_pos_x', 'norm_pos_y',
                                              'base_data', 'gaze_point_3d_x', 'gaze_point_3d_y', 'gaze_point_3d_z',
                                              'eye_center0_3d_x', 'eye_center0_3d_y', 'eye_center0_3d_z',
                                              'gaze_normal0_x', 'gaze_normal0_y', 'gaze_normal0_z',	'eye_center1_3d_x',
                                              'eye_center1_3d_y', 'eye_center1_3d_z', 'gaze_normal1_x',
                                              'gaze_normal1_y', 'gaze_normal1_z'])

# NOTE: This file path is designed to work on a Windows system. If you are using
# a Macintosh or Linux operating system, change the double backslashes into single
# forward slashes.
save_directory = os.path.dirname(os.path.realpath(__file__)) + '\\cleaned_files\\'
aoi_df.to_csv(save_directory + "cleaned_" + aoi_filename)
gaze_df.to_csv(save_directory + "cleaned_" + gaze_filename)

# Step 3: Convert the norm measurements from the gaze data into pixel data.
# The Pupil Labs world camera is set to record at 1280 x 720 resolution.
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

original_aoi_filename = aoi_filename

aoi_filename = save_directory + "cleaned_" + aoi_filename
gaze_filename = save_directory + "cleaned_" + gaze_filename

df_gaze = pd.read_csv(gaze_filename)
df_aoi = pd.read_csv(aoi_filename)
gaze_np = df_gaze.to_numpy()
aoi_np = df_aoi.to_numpy()

norm_x = gaze_np[:, 4]
norm_y = gaze_np[:, 5]

norm_x = (norm_x * CAMERA_WIDTH).astype(float)
norm_y = CAMERA_HEIGHT - (norm_y * CAMERA_HEIGHT).astype(float)

# Round pixel values since fractional pixels don't exist within the Dynamic AOI Toolkit output.
norm_x = np.round(norm_x, decimals=0)
norm_y = np.round(norm_y, decimals=0)

gaze_np[:, 4] = norm_x
gaze_np[:, 5] = norm_y

gaze_np = gaze_np[:, 1:]

gaze_df = pd.DataFrame(data=gaze_np, columns=['gaze_timestamp', 'world_index', 'confidence', 'norm_pos_x', 'norm_pos_y',
                                              'base_data', 'gaze_point_3d_x', 'gaze_point_3d_y', 'gaze_point_3d_z',
                                              'eye_center0_3d_x', 'eye_center0_3d_y', 'eye_center0_3d_z',
                                              'gaze_normal0_x', 'gaze_normal0_y', 'gaze_normal0_z',	'eye_center1_3d_x',
                                              'eye_center1_3d_y', 'eye_center1_3d_z', 'gaze_normal1_x',
                                              'gaze_normal1_y', 'gaze_normal1_z'])

# Write the updated values to a new csv file.
save_directory = os.path.dirname(os.path.realpath(__file__)) + '\\cleaned_files\\'
gaze_filename = save_directory + participant_identifier + "_transformed_gaze.csv"
gaze_df.to_csv(gaze_filename)


# Step 4: For each row, determine if the gaze position falls within the AOI.
df_gaze = pd.read_csv(gaze_filename)
gaze_np = df_gaze.to_numpy()

# This array stores the frames which are "hits," where the gaze falls within the AOI.
hits = np.zeros(np.shape(gaze_np)[0])

# Calculate the number of hits, as well as the first hit frame and last hit frame.
num_hits = 0
first_hit = None
last_hit = 0
for index, gaze_row in enumerate(gaze_np):
    aoi_row = aoi_np[index]

    gaze_x = gaze_row[4]
    gaze_y = gaze_row[5]

    aoi_x1 = aoi_row[4]
    aoi_x2 = aoi_row[5]
    aoi_y1 = aoi_row[6]
    aoi_y2 = aoi_row[7]

    if aoi_x1 <= gaze_x <= aoi_x2 and aoi_y1 <= gaze_y <= aoi_y2:
        hits[index] = 1
        num_hits += 1

        if first_hit is None:
            first_hit = index
        last_hit = index

hit_ratio = num_hits / hits.shape[0]
print(f"\nnumber of hits: {num_hits}\nhit ratio: {hit_ratio}\nfirst hit frame: {first_hit}\n"
      f"last hit frame: {last_hit}\n")

# Concatenate the hits numpy array to the aoi array.
hits = hits.reshape((np.shape(hits)[0], 1))

# This line is to resolve a bug where a single row is
# appended to aoi_np. The extra row is deleted if necessary.
if np.shape(aoi_np)[0] == (np.shape(hits)[0] + 1):
    aoi_np = np.delete(aoi_np, np.shape(aoi_np)[0] - 1, 0)

aoi_np = np.hstack((aoi_np, hits))
aoi_np = aoi_np[:, 1:]

aoi_df = pd.DataFrame(data=aoi_np, columns=['Frame', 'Object ID', 'category', 'x1', 'x2', 'y1', 'y2', 'type', 'hit'])
save_directory = os.path.dirname(os.path.realpath(__file__)) + '\\cleaned_files\\'
aoi_df.to_csv(save_directory + "hits_" + original_aoi_filename)

# Write information about the analysis to a text file.
output_file_name = save_directory + "participant_" + participant_identifier + "_analysis_results.txt"
aoi_info = open(output_file_name, "x")
aoi_info.write("number of hits: " + str(num_hits) + "\nhit ratio: " + str(hit_ratio)
               + "\ntotal rows: " + str(hits.shape[0]))
if num_hits > 0:
    aoi_info.write("\nfirst hit frame (first frame that the participant looked at an AOI): " + str(first_hit) +
                   "\nlast hit frame (last frame that the participant looked at an AOI): " + str(last_hit) + "\n")

print(f"\nSaved data to file: {output_file_name}\n")
aoi_info.close()
