export const fetchImage = async (url: string) => {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener('load', () => {
      resolve(image);
    });
    image.src = url;
  })
}

type GetSafeMediaSizeOpts = {
  width: number;
  height: number;
  maxWidth: number;
  maxHeight: number;
};
export const getSafeMediaSize = ({
  width,
  height,
  maxWidth,
  maxHeight,
}: GetSafeMediaSizeOpts): { width: number; height: number } => {
  const aspectRatio = width / height;
  const maxSize = Math.min(maxWidth, maxHeight);
  if (aspectRatio > 1) {
    // landscape
    return {
      width: maxSize,
      height: maxSize / aspectRatio,
    };
  } else {
    // portrait
    return {
      width: aspectRatio * maxSize,
      height: maxSize,
    };
  }
};
