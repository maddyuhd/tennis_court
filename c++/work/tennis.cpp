/* 
 * Author: maddy
 */
#include "opencv2/opencv.hpp"
#include "algorithm"
#include "string"
#include "vector"
using namespace cv;
using namespace std;

// helper function
void show(Mat src, string msg = "default message"){
    imshow(msg, src);
    waitKey(0);
}

// class lines_class{
//   public:
//     lines_class(vector lines);

//     Point GetPts() const;

//   private:
//     Point pt1, pt2, midpts;
// };

// lines_class::lines_class(vector lines){
//     float rho = lines[0][0], theta = lines[0][1];
//     double a = cos(theta), b = sin(theta);
//     double x0 = a*rho, y0 = b*rho;
//     pt1.x = cvRound(x0 + 1000*(-b));
//     pt1.y = cvRound(y0 + 1000*(a));
//     pt2.x = cvRound(x0 - 1000*(-b));
//     pt2.y = cvRound(y0 - 1000*(a));
//     midpts.x,midpts.y = () 
// }

// lines_class::GetPts() const
// {
//    return pt1, pt2;
// }

void detect_lines(Mat src, Mat resImg, bool debug = true){
  vector<Vec2f> lines;
  // detect lines
  HoughLines(src, lines, 1, 3*CV_PI/180, 90);//, 0, 0 );

  for( size_t i = 0; i < lines.size(); i++ )
  {
        float rho = lines[i][0], theta = lines[i][1];
        Point pt1, pt2;
        double a = cos(theta), b = sin(theta);
        double x0 = a*rho, y0 = b*rho;
        pt1.x = cvRound(x0 + 1000*(-b));
        pt1.y = cvRound(y0 + 1000*(a));
        pt2.x = cvRound(x0 - 1000*(-b));
        pt2.y = cvRound(y0 - 1000*(a));
        line( resImg, pt1, pt2, Scalar(0,0,255), 2);
  }

  if (debug){ show(resImg,"line");  }
}

Mat skeletonize(Mat src, bool debug = true){
  Mat element = getStructuringElement(MORPH_CROSS, Size (5,5));
  bool done = false;
  Mat er,temp;
  int zeros;
  int size = src.cols * src.rows;
  Mat skel(src.rows,src.cols, CV_8UC1, Scalar(0,0,0));

  while(!done){
    erode(src, er, element);
    dilate(er, temp, element);
    subtract(src, temp, temp);
    bitwise_or(skel, temp, skel);

    er.copyTo(src);

    zeros = size - countNonZero(src);

    if (zeros == size){
      done = true;
    }
  }
  // if (debug){ show(skel,"skel");  }
  return skel;
}

void preProcess(string imgPath, bool debug = true){
  Mat img = imread(imgPath);
  int w = img.cols; int h = img.rows;
  Mat resImg;
  resize(img,resImg,Size (w/2,h/2));
  
  Mat HSV;
  cvtColor(resImg, HSV, CV_BGR2HSV);

  Mat whiteThres;
  int x = 75;
  inRange(HSV, Scalar(0, 0, 255-x), Scalar(255, x, 255), whiteThres);

  if (debug){ show(whiteThres,"src");  }

  Mat skel = skeletonize(whiteThres);
  detect_lines(skel, resImg);


}

int main(int argc, char** argv) {
  string img_path[] = {"images/tennis_court.jpg", "images/test.jpg"};
  preProcess(img_path[0]);//change
  return 0;
}
