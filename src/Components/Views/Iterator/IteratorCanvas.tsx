import { mean } from 'lodash';
import React, { useCallback, useEffect, useRef } from 'react';
import styled from "styled-components";
import ITERABLE from '../../../iterables/iterable_lip_sort.json';
import useInterval from '../../../utils/hooks/useInterval';

const CANVAS_WIDTH = 500;
const CANVAS_HEIGHT = 500;
const MS_PER_ITERATION = 80;

const IteratorCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const ctx = useRef<CanvasRenderingContext2D>(null);
  useEffect(() => {
    if (!ctx.current) {
      // @ts-ignore
      ctx.current = canvasRef.current?.getContext('2d');
    }
  }, [])

  const frameCount = useRef<number>(0);
  const updateCanvas = useCallback(() => {
    if (!ctx.current) {
      return;
    }
    drawCanvas(ctx.current, frameCount.current);
    frameCount.current += 1;
  }, []);
  useInterval(updateCanvas, MS_PER_ITERATION);

  return (
    <Container>
      <Canvas ref={canvasRef} width={CANVAS_WIDTH} height={CANVAS_HEIGHT}/>
    </Container>
  );
}

const Container = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
`

type Coord = number[];
type LandmarksValues = {
  'chin': Coord[];
  'left_eyebrow': Coord[];
  'right_eyebrow': Coord[];
  'nose_bridge': Coord[];
  'nose_tip': Coord[];
  'left_eye': Coord[];
  'right_eye': Coord[];
  'top_lip': Coord[];
  'bottom_lip': Coord[];
}

interface IterableItem {
  src: string;
  avg_color: string;
  description: string;
  face_box: {
    x: number,
    y: number,
    width: number,
    height: number,
    norm_x: number,
    norm_y: number,
    norm_width: number,
    norm_height: number
  },
  landmarks: {
    values: LandmarksValues,
    norm: LandmarksValues,
  },
}

const ITEMS_TO_DRAW: IterableItem[] = ITERABLE.iterable;
interface DrawableItem extends IterableItem {
  image: HTMLImageElement;
};
const itemsToDraw: DrawableItem[] = [
  ...ITEMS_TO_DRAW
].map((item) => {
  // Preload the image
  const image = new Image();
  image.src = item.src;
  return {
    ...item,
    image
  };
});

const FOCAL_POINT_BOX = {
  norm_x: 0.5,
  norm_y: 0.5,
  norm_width: 0.3,
  // norm_height: 0.3,
};

type Landmark =
'chin' |
'left_eyebrow' |
'right_eyebrow' |
'nose_bridge' |
'nose_tip' |
'left_eye' |
'right_eye' |
'top_lip' |
'bottom_lip';

const getDrawableCenterNorm = (item: DrawableItem, landmarksToAverage?: Landmark[]) => {
  const { face_box, landmarks } = item;
  if (!landmarksToAverage || !landmarksToAverage.length) {
    // normalize to face
    return {
      x: (face_box.norm_width / 2 + face_box.norm_x),
      y: (face_box.norm_height / 2 + face_box.norm_y),
    }
  }
  const xVals: number[] = [];
  const yVals: number[] = [];
  landmarksToAverage.forEach(key => {
    const values = landmarks.norm[key]
    values.forEach(([x, y]) => {
      xVals.push(x)
      yVals.push(y)
    });
  })
  return {
    x:  mean(xVals),
    y: mean(yVals),
  }
};

const drawItem = (ctx: CanvasRenderingContext2D, item: DrawableItem) => {
  const { image, face_box } = item;
  const canvas = ctx.canvas;
  // scale image such that all face boxes are the same width
  const targetBoxWidth = FOCAL_POINT_BOX.norm_width * canvas.width;
  const faceBoxWidth = image.naturalWidth * face_box.norm_width;
  const scaleFactor =  targetBoxWidth / faceBoxWidth;

  const imgWidth = image.naturalWidth * scaleFactor;
  const imgHeight = image.naturalHeight * scaleFactor;

  const drawableCenterNorm = getDrawableCenterNorm(item, ['top_lip', 'bottom_lip']);//, 'right_eye'])
  const drawableCenter = {
    x: imgWidth * drawableCenterNorm.x,
    y: imgHeight * drawableCenterNorm.y
  };

  const targetCoordCanvas = {
    x: FOCAL_POINT_BOX.norm_x * canvas.width,
    y: FOCAL_POINT_BOX.norm_y * canvas.height,
  }
  const x = targetCoordCanvas.x - drawableCenter.x;
  const y = targetCoordCanvas.y - drawableCenter.y;
  
  ctx.drawImage(image, x, y, imgWidth, imgHeight);
  ctx.lineWidth = 4;
  ctx.strokeStyle = 'red';
  
  // // draw face_box
  // const faceBox = {
  //   x: x + imgWidth * face_box.norm_x,
  //   y: y + imgHeight * face_box.norm_y,
  //   width: imgWidth * face_box.norm_width,
  //   height: imgHeight * face_box.norm_height,
  // }
  // ctx.strokeRect(faceBox.x, faceBox.y, faceBox.width, faceBox.height);
}

const drawCanvas = (ctx: CanvasRenderingContext2D, frameCount: number) => {
  const canvas = ctx.canvas;
  const loadedImages = itemsToDraw.filter(item => item.image.complete);
  const item = loadedImages[frameCount % loadedImages.length]
  if (item) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawItem(ctx, item);
  }
}

const Canvas = styled.canvas``

export default IteratorCanvas;