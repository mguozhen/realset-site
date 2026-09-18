DRIVE_ROOT = "1pGbE3PYFHM9wjv6xVHkMBwoPJbEbH4ot"
MIRRORS = [("Baidu Pan (China mirror)", "https://pan.baidu.com/s/1Pr3g6z42Xf_zQG71wrM0Nw?pwd=np82", "code np82"),
           ("MultCloud (private link)", "https://share.multcloud.link/share/223968a3-bc0e-47fb-8d48-860281724e1f", "password 8iUc")]
# Embodied sample packs, one per Drive folder. contents = what a buyer will find inside.
PACKS = [
 dict(slug="ego-exo-paired", k="Body · 01", name="Ego-Exo Paired", drive="1pJhuf45ET6w7eXATstXlP7nvqVjU2pHg", n=5,
  summary="Synchronized first-person (head-mounted) and third-person capture of the same task, for cross-view policy learning and video-to-action pretraining.",
  contents=["bike_mechanic, carfix: skilled repair work", "factory_0001, factory_0002: light assembly line", "third-person exo rig alongside the ego stream"],
  spec=[("Views","Ego (head-mounted) + Exo (fixed third-person), time-aligned"),("Video","1920×1080, 30 fps"),("Extras","Camera intrinsics, per-frame JPGs on request"),("Delivery","Raw + undistorted video, LeRobot packaging optional")]),
 dict(slug="ego-dual-wrist", k="Body · 02", name="Ego Dual-Wrist", drive="1j3iE_8pD0DE7yGqwi1StVholbTlB4gB3", n=7,
  summary="Head camera plus two wrist-mounted cameras during household manipulation. Both hands in frame at all times, the view a bimanual robot actually needs.",
  contents=["arrange_flowers, folding_socks, Making_Tea", "Clean the screen (2 takes), Tending to potted plants", "new sample: latest rig revision"],
  spec=[("Views","Head + left wrist + right wrist"),("Video","1920×1080, 30 fps, synchronized"),("Tasks","Household: folding, cleaning, plants, tea"),("Delivery","Raw video + action segments")]),
 dict(slug="ego-pose-retargeting", k="Body · 03", name="Processed Ego: Hand Pose + Retargeting", drive="1Njqb-N5T2HTeVxE59ry2qa-nKq9KXSMd", n=9,
  summary="Ego video processed into 3D hand pose (MANO), camera trajectory with dense depth, and atomic action annotations, then retargeted to a robot hand. This is the pack with the fullest processing pipeline.",
  contents=["3 raw_video_* folders: raw + undistorted video, frames, intrinsics", "camera_traj.npz (cam_c2w, depths, K) and hands.npz (MANO pose, betas, wrist trans/rot in world and camera frames, validity mask)", "ego_action_annotation.json: verb + object + description + bbox + confidence per segment", "demo videos: human-to-robot retargeting (hamer), 4-panel fold / weigh / 10-min, physics 2×2", "README_数据说明.md: full field reference"],
  spec=[("Hand pose","MANO 15-joint axis-angle, both hands, world + camera frames"),("Camera","Per-frame c2w pose, dense depth, refined intrinsics + FOV"),("Annotation","Atomic actions with timestamps, frames, bbox (0–1000), confidence"),("Formal batches","Add raw IMU (gyro + accel), LeRobot packaging on request"),("Privacy","Capture staff anonymized")]),
 dict(slug="internet-ego", k="Body · 04", name="Internet Ego", drive="1_GrweFQs433yz66xIZOniBv3e7KfHKQP", n=8,
  summary="Curated first-person clips sourced from the open web, filtered for manipulation-relevant content. Cheap breadth for pretraining, not for fine-grained labels.",
  contents=["8 clips, mixed household and hobby tasks"],
  spec=[("Source","Public web video, filtered"),("Use","Pretraining / diversity"),("Labels","None in sample; segmentation available on request"),("Rights","Provided for evaluation only; licensing terms per batch")]),
 dict(slug="umi-gripper", k="Body · 05", name="UMI Gripper", drive="1f3Jkh-HAYs6MN93itlD3MN_wILusAa4p", n=4,
  summary="Handheld UMI-style gripper demonstrations with fisheye wrist camera, the format used directly by diffusion-policy training.",
  contents=["folding towel (folder with full episode)", "multi-cam, making coffee, stacking book (mp4)"],
  spec=[("Rig","Handheld gripper with wrist camera"),("Tasks","Towel folding, coffee, book stacking"),("Delivery","Video + gripper trajectory")]),
 dict(slug="robot-teleop-lerobot", k="Body · 06a", name="Robot Teleop, LeRobot format", drive="1CfV_Vpqcr_Gw7dqrMqpc4j5ET-_iih8V", n=9,
  summary="Bimanual teleoperation episodes exported in LeRobot v2 format: multi-camera video plus joint states and actions, ready to load into a training script.",
  contents=["erase_a_table, fold_towel, hand_over_flower, open_a_lunchbag", "pick and place: toothbrushes, fruits into containers", "pick_the_hammer_and_hit_desk, pull_out_tissue, take_a_notebook_from_a_person"],
  spec=[("Format","LeRobot v2 dataset folder"),("Streams","Multi-camera video, joint states, gripper, actions"),("Episodes","9 task families in sample"),("Delivery","Per-episode QC, retake rules agreed up front")]),
 dict(slug="robot-teleop-mcap", k="Body · 06b", name="Robot Teleop, MCAP format", drive="1GRa7llZ-13oxJAV1wIUjqCnEjP_QVDk1", n=3,
  summary="The same teleop pipeline exported as ROS-style MCAP bags for teams that ingest raw topics rather than LeRobot.",
  contents=["Folding clothes, grab orange bottle, grab small white ball"],
  spec=[("Format","MCAP (ROS 2 topics)"),("Streams","Camera topics, joint states, commands"),("Delivery","Convertible to LeRobot or RLDS")]),
 dict(slug="spatial-360", k="Body · 07", name="Spatial 360", drive="1hnoQDTwsEoTSH-7wVNJeVorDGU9PbQeY", n=5,
  summary="360° captures and point clouds of real environments (home, office, a postal facility in the Bay Area) for scene understanding and simulation reconstruction.",
  contents=["Cottage, Office, postal-facility scenes", "ply point clouds", "Raw_360_INSV (Insta360 raw)"],
  spec=[("Capture","Insta360 raw + stitched"),("Outputs","PLY point cloud per scene"),("Use","Scene reconstruction, sim asset building")]),
]
# Non-embodied lines: samples on request (no public link yet)
REQUEST_ONLY = [
 dict(k="Field", name="Coding agent RL environments & SWE benchmarks", summary="ProgramBench, DeepSWE, FrontierSWE, SWE-Atlas QnA, Terminal Bench 2, SWE PRO. Verifiable environments with tests or continuous scores; 50 items/day per pipeline.", status="Samples on request"),
 dict(k="Field", name="Computer-use & tool-calling trajectories", summary="WebArena-infinity, OSWorld 2.0 long-horizon tasks with verifiers; skills SFT/RL trajectories; tool-generalization sets.", status="Samples on request"),
 dict(k="Field", name="Claude coding session data (cleaned)", summary="De-identified coding agent sessions. Released only after licensing and consent review; samples are provided under NDA to qualified labs.", status="Under compliance review"),
 dict(k="Judge", name="Expert rubric data (medical, finance)", summary="Rubric-annotated expert judgments produced in the Realset Workspace.", status="Samples on request"),
]

# Bucket-hosted large sample packs (S3-compatible delivery). Credentials are issued per client, never on the page.
BUCKET_PACKS = [
 dict(slug="ego-hand-5h", k="Body · 08", name="Ego Hand Manipulation, 5-hour LeRobot sample", n="390 episodes",
  summary="Five hours of first-person bimanual manipulation with per-frame 3D hand pose (MANO), wrist pose, camera intrinsics and extrinsics, packaged as a LeRobot v2.1 dataset. Ready to load into a training script.",
  stats=[("Episodes","390"),("Frames","541,192 at 30 fps (5.0 h)"),("Tasks","231 distinct task strings"),("Video","1440×1920 egocentric RGB, H.264, one mp4 per episode"),("Episode length","150 – 21,045 frames, median 874 (~29 s)"),("Size","22.3 GiB · 793 objects"),("Format","LeRobotDataset v2.1: data/*.parquet · videos/ · meta/ · calibration/ · visualization/")],
  features=[("observation.images.ego","video [1440,1920,3]","egocentric RGB"),("observation.state","float64 [122]","left 61 + right 61: wrist pos (cam), root rot, 15 joint eulers, MANO betas"),("left/right_transl_world","float64 [3]","wrist translation, world frame, metres"),("left/right_orient_world","float64 [9]","wrist rotation 3×3 row-major"),("left/right_hand_pose","float64 [135]","15 MANO joint rotations, 3×3 each"),("left/right_per_frame_validity","float64 [1]","tracking validity per frame"),("state_mask","bool [2]","which hands present"),("intrinsics / extrinsics_w2c / fov","float64 [9] / [16] / [2]","per-frame camera model, OpenCV convention")],
  previews=[("vis_episode_000000.mp4","Episode 0 — wrist axes, fingertips and task HUD projected onto the ego video"),("vis_episode_000016.mp4","Episode 16 — second camera configuration (fx≈871)")],
  access_cmd="aws s3 sync s3://&lt;bucket&gt;/&lt;prefix&gt;/ ./ego-hand-5h/ --endpoint-url &lt;endpoint&gt; --profile realset",
  guide=["ACCESS_GUIDE.md: aws cli and rclone setup, subset download (meta/ first, a few MB)","MANIFEST.txt: 793 objects with byte counts for post-download verification","README.md + ACTION_DATA_DESCRIPTION.md: feature table, coordinate frames, MANO conventions, calibration","visualization/visualize.py: projects the delivered 3D hands onto the ego video, frame by frame"],
  json="ego_hand_5h.json"),
]
