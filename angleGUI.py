import datetime
import os
import tkinter as tk
from tkinter import messagebox, ttk

import cv2
import matplotlib.pyplot as plt
import numpy as np

outFile = ""


def start(videoPath, outputDir):
    # Create directory if it doesn't exist
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    # Open file, create if it doesn't exist
    global outFile
    outFile = "{}/{}.csv".format(outputDir,
                                 datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    f = open(outFile, "w+")

    live = True
    if videoPath == "Video Path" or videoPath == "":
        # Start live video capture
        f.write("Time,Angle\n")
        cap = cv2.VideoCapture(0)
    else:
        # Open video file
        live = False
        f.write("Frame,Angle\n")
        cap = cv2.VideoCapture(videoPath)

    frameCount = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frameCount += 1
        if frameCount == 1:
            # Select ROI
            r = cv2.selectROI(frame)

            # Crop image
            frame = frame[int(r[1]):int(r[1] + r[3]),
                          int(r[0]):int(r[0] + r[2])]
            frame = cv2.GaussianBlur(frame, (5, 5), 0)

            # Select point for width
            p = cv2.selectROI(frame)
            width = p[2]
            pivot = [p[0]+p[2], 0]

            # Select point for terminal
            term = cv2.selectROI(frame)
            term = [int((term[1] + term[3]) / 2), int((term[0] + term[2]) / 2)]

            # Select point for color
            pColor = cv2.selectROI(frame)
            centerVal = frame[int(pColor[1] + pColor[3] / 2),
                              int(pColor[0] + pColor[2] / 2)]

            continue

        # Crop image
        frame = frame[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        frame_out = frame.copy()

        # Blur the image for better edge detection
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        frame_out = cv2.GaussianBlur(frame_out, (5, 5), 0)

        # Create a mask for values around centerVal
        mask = cv2.inRange(frame, centerVal - 15, centerVal + 15)

        # Implement mask
        frame = cv2.bitwise_and(frame, frame, mask=mask)

        # Convert to grayscale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply thresholding
        frame = cv2.threshold(frame, 20, 255, cv2.THRESH_BINARY)[1]

        # Remove small objects
        kernel = np.ones((2, 2), np.uint8)
        frame = cv2.erode(frame, kernel, iterations=2)
        frame = cv2.dilate(frame, kernel, iterations=2)

        # Pivot point
        pivot[1] = frame.shape[1] - 1 - \
            np.argmax(frame[::-1][int(p[0]+p[2]/2)]) - int(width)

        # Terminal point
        # Take vertical slices of the image from right to left
        for i in range(frame.shape[1] - 1, 0, -1):
            # If the slice contains a white pixel
            if np.max(frame[:, i]) > 0:
                term = [i, frame.shape[0] - 1 -
                        np.argmax(frame[::-1][i-int(width/2)]) - int(width)]
                break

        # Calculate angle
        if pivot[0] - term[0] == 0:
            angle = 0
        else:
            angle = np.arctan((pivot[0] - term[0]) /
                              (pivot[1] - term[1])) * 180 / np.pi

        # Write to file
        if live:
            f.write("{},{}\n".format(
                datetime.datetime.now().strftime("%H-%M-%S"), angle))
        else:
            f.write("{},{}\n".format(frameCount, angle))

        # Draw pivot point
        cv2.circle(frame_out, pivot, 4, (255, 0, 0), 0)

        # Draw terminal point
        cv2.circle(frame_out, term, 4, (255, 0, 0), 0)

        # Draw line between pivot and terminal
        cv2.line(frame_out, pivot, term, (0, 0, 255), 2)

        # Display the resulting frame
        cv2.imshow("Frame", frame_out)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture
    cap.release()
    f.close()
    cv2.destroyAllWindows()
    messagebox.showinfo("Done", "Done")


def plot():
    global outFile
    data = np.loadtxt(outFile, delimiter=",", skiprows=1)
    plt.plot(data[:, 0], data[:, 1])
    plt.xlabel("Frame")
    plt.ylabel("Angle")
    plt.show()


def main():
    # Create window
    window = tk.Tk()
    window.title("Angle GUI")

    # Create video path input
    videoPathLabel = ttk.Label(window, text="Video Path")
    videoPathLabel.grid(column=0, row=0)
    videoPathInput = ttk.Entry(window, width=50)
    videoPathInput.grid(column=1, row=0)
    videoPathInput.insert(0, "Video Path")

    # Create output directory input
    outputDirLabel = ttk.Label(window, text="Output Directory")
    outputDirLabel.grid(column=0, row=1)
    outputDirInput = ttk.Entry(window, width=50)
    outputDirInput.grid(column=1, row=1)
    outputDirInput.insert(0, "./data")

    # Create start button
    startButton = ttk.Button(window, text="Start", command=lambda: start(
        videoPathInput.get(), outputDirInput.get()))
    startButton.grid(column=0, row=2)

    # Create plot button
    plotButton = ttk.Button(window, text="Plot", command=lambda: plot())
    plotButton.grid(column=1, row=2)

    # Run window
    window.mainloop()


if __name__ == "__main__":
    main()
