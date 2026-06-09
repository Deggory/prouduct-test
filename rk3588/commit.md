Root folder
Commit	Name	Files changed
f9ee8ea	Remove PNG files from Git LFS tracking	.gitattributes
b51be4e	feat(selfdrive): Make op run	.gitmodules, README.md, docs/assets/ops_cuda.png, opendbc_repo
4c65f7d	chore(readme): Update readme	README.md
306a880	feat(locationd): Allow no imu	README.md
3ad69b2	fix(lon): Change LEAD_DANGER_FACTOR	README.md
selfdrive/
Commit	Name	Subfolder	Files changed
f9ee8ea	Remove PNG files from Git LFS tracking	selfdrive/assets/	many .png images under images/, offroad/, training/
b51be4e	feat(selfdrive): Make op run	selfdrive/locationd/	locationd.py
b51be4e	feat(selfdrive): Make op run	selfdrive/modeld/	SConscript, dmonitoringmodeld.py, modeld.py
b51be4e	feat(selfdrive): Make op run	selfdrive/selfdrived/	selfdrived.py
6e91b9c	feat(tools): Support old local route	selfdrive/debug/	uiview.py
28b99cc	feat(lon): Opt lon control	selfdrive/car/	cruise.py
28b99cc	feat(lon): Opt lon control	selfdrive/controls/lib/	longitudinal_planner.py
28b99cc	feat(lon): Opt lon control	selfdrive/controls/lib/longitudinal_mpc_lib/	long_mpc.py
f39cc16	feat(more): Adapter to rk3588	selfdrive/locationd/	calibrationd.py
f39cc16	feat(more): Adapter to rk3588	selfdrive/modeld/	modeld.py
f39cc16	feat(more): Adapter to rk3588	selfdrive/selfdrived/	selfdrived.py
95af03c	feat(camera): Change camera focal	selfdrive/selfdrived/	selfdrived.py
95af03c	feat(camera): Change camera focal	selfdrive/ui/	ui.h
bf3f07e	feat(ui): Adapter ui size to 800x400	selfdrive/ui/qt/	many UI files: body.cc, qt_window.*, sidebar.*, offroad/onroad/widgets/setup files
bf3f07e	feat(ui): Adapter ui size to 800x400	selfdrive/ui/sunnypilot/qt/	settings panels, sidebar, widgets, networking
bf3f07e	feat(ui): Adapter ui size to 800x400	selfdrive/ui/translations/	main_ar.ts, main_de.ts, main_es.ts, main_fr.ts, main_ja.ts, main_ko.ts, main_pt-BR.ts, main_th.ts, main_tr.ts, main_zh-CHS.ts, main_zh-CHT.ts
712bcb2	feat(camera): Change camera focal to imx415	selfdrive/ui/	ui.h
306a880	feat(locationd): Allow no imu	selfdrive/locationd/	locationd.py
ddf8fa4	fix(lon): Opt lon ctrl	selfdrive/controls/lib/longitudinal_mpc_lib/	long_mpc.py
3ad69b2	fix(lon): Change LEAD_DANGER_FACTOR	selfdrive/controls/lib/longitudinal_mpc_lib/	long_mpc.py
common/
Commit	Name	Subfolder	Files changed
f39cc16	feat(more): Adapter to rk3588	common/	realtime.py
95af03c	feat(camera): Change camera focal	common/transformations/	camera.py
712bcb2	feat(camera): Change camera focal to imx415	common/transformations/	camera.py
cereal/
Commit	Name	Subfolder	Files changed
f39cc16	feat(more): Adapter to rk3588	cereal/messaging/	__init__.py
f39cc16	feat(more): Adapter to rk3588	cereal/	services.py
system/
Commit	Name	Subfolder	Files changed
b51be4e	feat(selfdrive): Make op run	system/manager/	process_config.py
tools/
Commit	Name	Subfolder	Files changed
f9ee8ea	Remove PNG files from Git LFS tracking	tools/bodyteleop/static/	poster.png
f9ee8ea	Remove PNG files from Git LFS tracking	tools/cabana/assets/	cabana-icon.png
b51be4e	feat(selfdrive): Make op run	tools/	install_ubuntu_dependencies.sh
b51be4e	feat(selfdrive): Make op run	tools/webcam/	camera.py, camerad.py
6e91b9c	feat(tools): Support old local route	tools/car_porting/	auto_fingerprint.py
6e91b9c	feat(tools): Support old local route	tools/lib/	route.py
6e91b9c	feat(tools): Support old local route	tools/plotjuggler/	juggle.py
cab810f	fix(tools): Fix tools	tools/plotjuggler/	README.md, pic/dir.png, pic/juggler.png

Main RK3588-related commits are:

b51be4e, 6e91b9c, cab810f, f39cc16, 95af03c, bf3f07e, 712bcb2, 306a880.
