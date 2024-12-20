#include <QApplication>
#include <QMainWindow>
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QFileDialog>
#include <QLabel>
#include <QPixmap>
#include <QVBoxLayout>
#include <QPushButton>
#include <QScrollArea>
#include <QImage>
#include <QPainter>
#include <iostream>
#include <QMouseEvent>

class ImageBox : public QLabel {
    Q_OBJECT

public:
    ImageBox(QWidget *parent = 0) : QLabel(parent), selecting(false) {
        setAlignment(Qt::AlignTop | Qt::AlignLeft);
        setStyleSheet("background-color: white;");
    }

    void setImage(const QImage &img) {
        image = img;
        setPixmap(QPixmap::fromImage(image));
    }

protected:
    void mousePressEvent(QMouseEvent *event) override {
        start_x = end_x = event->x();
        start_y = end_y = event->y();
        selecting = true;
    }

    void mouseMoveEvent(QMouseEvent *event) override {
        if (selecting) {
            end_x = event->x();
            end_y = event->y();
            update();
        }
    }

    void mouseReleaseEvent(QMouseEvent *event) override {
        selecting = false;
        update();
    }

    void paintEvent(QPaintEvent *event) override {
        QLabel::paintEvent(event);
        if (selecting) {
            QPainter painter(this);
            painter.setPen(Qt::yellow);
            painter.drawRect(start_x, start_y, end_x - start_x, end_y - start_y);
        }
    }

public:
    void getSelection(int &x, int &y, int &w, int &h) {
        x = start_x;
        y = start_y;
        w = end_x - start_x;
        h = end_y - start_y;
    }

private:
    QImage image;
    bool selecting;
    int start_x, start_y, end_x, end_y;
};

class ImageTrimmerApp : public QMainWindow {
    Q_OBJECT

public:
    ImageTrimmerApp() {
        resize(1300, 850);

        QMenu *fileMenu = menuBar()->addMenu(tr("ファイル"));
        QAction *openAct = fileMenu->addAction(tr("画像を開く"));
        QAction *trimAct = fileMenu->addAction(tr("選択範囲をトリミング"));
        QAction *saveAllAct = fileMenu->addAction(tr("すべてのトリミングを保存"));
        QAction *exitAct = fileMenu->addAction(tr("終了"));

        imageBox = new ImageBox(this);

        QPushButton *trimButton = new QPushButton(tr("選択範囲をトリミング"));
        QPushButton *clearButton = new QPushButton(tr("選択範囲をクリア"));

        QVBoxLayout *layout = new QVBoxLayout;
        layout->addWidget(imageBox);
        layout->addWidget(trimButton);
        layout->addWidget(clearButton);

        QWidget *container = new QWidget;
        container->setLayout(layout);

        QScrollArea *scrollArea = new QScrollArea;
        scrollArea->setWidget(container);
        setCentralWidget(scrollArea);

        connect(openAct, &QAction::triggered, this, &ImageTrimmerApp::openImage);
        connect(trimAct, &QAction::triggered, this, &ImageTrimmerApp::trimImage);
        connect(saveAllAct, &QAction::triggered, this, &ImageTrimmerApp::saveAllTrims);
        connect(exitAct, &QAction::triggered, this, &QWidget::close);
        connect(trimButton, &QPushButton::clicked, this, &ImageTrimmerApp::trimImage);
        connect(clearButton, &QPushButton::clicked, this, &ImageTrimmerApp::clearSelections);
    }

private slots:
    void openImage() {
        QString filePath = QFileDialog::getOpenFileName(this, tr("画像を開く"), "", tr("Images (*.jpg *.png)"));
        if (!filePath.isEmpty()) {
            QImage image(filePath);
            imageBox->setImage(image);
        }
    }

    void trimImage() {
        int x, y, w, h;
        imageBox->getSelection(x, y, w, h);
        if (w > 0 && h > 0) {
            std::cout << "トリミング: x=" << x << " y=" << y << " w=" << w << " h=" << h << std::endl;
        }
    }

    void saveAllTrims() {
        std::cout << "すべてのトリミングを保存" << std::endl;
    }

    void clearSelections() {
        std::cout << "選択範囲をクリア" << std::endl;
    }

private:
    ImageBox *imageBox;
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    ImageTrimmerApp window;
    window.show();
    return app.exec();
}

#include "main.moc"