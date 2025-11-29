import os
import numpy as np

# Folder containing your pose .npz files
POSES_FOLDER = "captured_poses_npz"

def load_poses_as_list_of_lists(folder: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    poses_dir = os.path.join(base_dir, folder)

    files = sorted(
        [f for f in os.listdir(poses_dir) if f.lower().endswith(".npz")]
    )

    all_poses = []

    for fname in files:
        path = os.path.join(poses_dir, fname)
        data = np.load(path)

        # Adjust this depending on how your .npz is structured:
        # Common patterns:
        #   - single array: use list(data.values())[0]
        #   - named 'pose' or 'T': data['pose'] or data['T']
        if len(data.files) == 1:
            arr = data[data.files[0]]
        else:
            # Prefer a key name if it exists, otherwise first entry
            key = 'pose' if 'pose' in data.files else data.files[0]
            arr = data[key]

        # Flatten to 1D then convert to a plain Python list
        all_poses.append(arr.flatten().tolist())

    return all_poses

if __name__ == "__main__":
    world_points_list = load_poses_as_list_of_lists(POSES_FOLDER)

    # Print in the visual form you showed
    print("[")
    for row in world_points_list:
        print("    " + str(row) + ",")
    print("]")

    # If you want a NumPy array compatible with cv2:
    world_points = np.array(world_points_list, dtype=np.float32)
    print("\nNumPy shape:", world_points.shape)