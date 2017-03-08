import os, sys
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# SPHARM
#

class SPHARM(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "SPHARM"
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Laura Pascal (Kitware Inc.)"]
    self.parent.helpText = """
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
    """ # replace with organization, grant and thanks.

#
# SPHARMWidget
#

class SPHARMWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    #
    #  Interface
    #
    loader = qt.QUiLoader()
    self.moduleName = 'SPHARM'
    scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
    scriptedModulesPath = os.path.dirname(scriptedModulesPath)
    path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.moduleName)
    qfile = qt.QFile(path)
    qfile.open(qt.QFile.ReadOnly)
    widget = loader.load(qfile, self.parent)
    self.layout = self.parent.layout()
    self.widget = widget
    self.layout.addWidget(widget)


    # Global variables of the Interface
    #     SegPostProcess: Parameters Area
    self.InputData = self.getWidget('InputDataLineEdit')
    self.applyButton = self.getWidget('applyButton')

    # Connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
#    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
#    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Refresh Apply button state
    # self.onSelect()

  def cleanup(self):
    pass

#   def onSelect(self):
#    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

    # Functions to recovery the widget in the .ui file
  def getWidget(self, objectName):
    return self.findWidget(self.widget, objectName)

  def findWidget(self, widget, objectName):
    if widget.objectName == objectName:
      return widget
    else:
      for w in widget.children():
        resulting_widget = self.findWidget(w, objectName)
        if resulting_widget:
          return resulting_widget
    return None

  def onApplyButton(self):
    self.callSegPostProcess()
    self.callGenParaMesh()

  def callSegPostProcess(self):
    #     Creation of the command line
    SegPostProcess = "/home/laura/Documents/SPHARM/SPHARM-PDM-build/SPHARM-PDM-build/SegPostProcessCLP"
    arguments = list()
    input = self.InputData.currentPath
    arguments.append(input)
    output = slicer.app.temporaryPath + "/outputPostProcess.gipl"
    arguments.append(output)
    # arguments.append("--label")
    # arguments.append("1")
    # arguments.append("--space")
    # arguments.append("0.5,0.5,0.5")
    #     Call the executable
    process = qt.QProcess()
    print "Calling " + os.path.basename(SegPostProcess)
    # process.setStandardErrorFile(setStandardErrorFilelicer.app.temporaryPath + "/mylog.log", qt.QIODevice.Append)
    # process.setStandardOutputFile(slicer.app.temporaryPath + "/mylogOutputFile.log", qt.QIODevice.Append)
    process.start(SegPostProcess, arguments)
    process.waitForStarted()
    print "state: " + str(process.state())
    process.waitForFinished()
    print "error: " + str(process.error())
    print "exitStatus: " + str(process.exitStatus())

  def callGenParaMesh(self):
    #     Creation of the command line
    GenParaMesh = "/home/laura/Documents/SPHARM/SPHARM-PDM-build/SPHARM-PDM-build/GenParaMeshCLP"
    arguments = list()
    input = slicer.app.temporaryPath + "/outputPostProcess.gipl"
    arguments.append(input)
    output = slicer.app.temporaryPath + "/Parameterization.vtk"
    arguments.append(output)
    output = slicer.app.temporaryPath + "/SurfaceMesh.vtk"
    arguments.append(output)
    #     Call the executable
    process = qt.QProcess()
    print "Calling " + os.path.basename(GenParaMesh)
    process.setStandardErrorFile(slicer.app.temporaryPath + "/mylog.log", qt.QIODevice.Append)
    process.setStandardOutputFile(slicer.app.temporaryPath + "/mylogOutputFile.log", qt.QIODevice.Append)
    process.start(GenParaMesh, arguments)
    process.waitForStarted()
    print "state: " + str(process.state())
    process.waitForFinished()
    print "error: " + str(process.error())
    print "exitStatus: " + str(process.exitStatus())

  def callParaToSPHARMMesh(self):
    #     Creation of the command line
    ParaToSPHARMMesh = "/home/laura/Documents/SPHARM/SPHARM-PDM-build/SPHARM-PDM-build/ParaToSPHARMMeshCLP"
    arguments = list()
    input = slicer.app.temporaryPath + "/SurfaceMesh.vtk"
    arguments.append(input)
    input = slicer.app.temporaryPath + "/Parameterization.vtk"
    arguments.append(input)
    output = slicer.app.temporaryPath
    arguments.append(output)
    #     Call the executable
    process = qt.QProcess()
    print "Calling " + os.path.basename(ParaToSPHARMMesh)
    # process.setStandardErrorFile(slicer.app.temporaryPath + "/mylog.log", qt.QIODevice.Append)
    # process.setStandardOutputFile(slicer.app.temporaryPath + "/mylogOutputFile.log", qt.QIODevice.Append)
    process.start(ParaToSPHARMMesh, arguments)
    process.waitForStarted()
    print "state: " + str(process.state())
    process.waitForFinished()
    print "error: " + str(process.error())
    print "exitStatus: " + str(process.exitStatus())



#
# SPHARMLogic
#

class SPHARMLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  pass




class SPHARMTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.assertTrue(self.test_SPHARM1())
    self.delayDisplay(' Tests Passed! ')

  def test_SPHARM1(self):
    self.delayDisplay("Starting the test")
    #     Creation of the command line
    CLITest = "/home/laura/Documents/Slicer/Slicer-build/Slicer-build/lib/Slicer-4.7/cli-modules/GaussianBlurImageFilter"
    arguments = list()
    input = "/home/laura/Documents/Data/NRRD_Files/MRHead.nrrd"
    arguments.append(input)
    output = slicer.app.temporaryPath + "/MRHead_GaussianFilter.nrrd"
    arguments.append(output)
    #     Call the executable
    process = qt.QProcess()
    print "Calling " + os.path.basename(CLITest)
    process.start(CLITest, arguments)
    process.waitForStarted()
    if process.state() == 2:
      process.waitForFinished()
      if process.exitStatus() == 0:
        return True
      else:
        return False
    else:
      return False