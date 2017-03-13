import os, sys
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# ShapeAnalysisModule
#

class ShapeAnalysisModule(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Shape Analysis Module"
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
# ShapeAnalysisModuleWidget
#

class ShapeAnalysisModuleWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    #
    #  Interface
    #
    loader = qt.QUiLoader()
    self.moduleName = 'ShapeAnalysisModule'
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
    #   Group Project IO
    self.GroupProjectInputDirectory = self.getWidget('DirectoryButton_GroupProjectInputDirectory')
    self.RandomizeInputs = self.getWidget('checkBox_RandomizeInputs')
    self.GroupProjectOutputDirectory = self.getWidget('DirectoryButton_GroupProjectOutputDirectory')
    self.Debug = self.getWidget('checkBox_Debug')
    #   Post Processed Segmentation
    self.OverwriteSegPostProcess = self.getWidget('checkBox_OverwriteSegPostProcess')
    self.RescaleSegPostProcess = self.getWidget('checkBox_RescaleSegPostProcess')
    self.sx = self.getWidget('SliderWidget_sx')
    self.sy = self.getWidget('SliderWidget_sy')
    self.sz = self.getWidget('SliderWidget_sz')
    self.LabelState = self.getWidget('checkBox_LabelState')
    self.label_ValueLabelNumber = self.getWidget('label_ValueLabelNumber')
    self.ValueLabelNumber = self.getWidget('SliderWidget_ValueLabelNumber')
    #   Generate Mesh Parameters
    self.OverwriteGenParaMesh = self.getWidget('checkBox_OverwriteGenParaMesh')
    self.NumberofIterations = self.getWidget('SliderWidget_NumberofIterations')
    #   Parameters to SPHARM Mesh
    self.OverwriteParaToSPHARMMesh = self.getWidget('checkBox_OverwriteParaToSPHARMMesh')
    self.SubdivLevelValue = self.getWidget('SliderWidget_SubdivLevelValue')
    self.SPHARMDegreeValue = self.getWidget('SliderWidget_SPHARMDegreeValue')
    self.thetaIterationValue = self.getWidget('spinBox_thetaIterationValue')
    self.phiIterationValue = self.getWidget('spinBox_phiIterationValue')
    self.medialMesh = self.getWidget('checkBox_medialMesh')
    #   Visualization
    #   Apply CLIs
    self.applyButton = self.getWidget('applyButton')

    # Connections
    #   Group Project IO
    #   Post Processed Segmentation
    self.LabelState.connect('clicked(bool)', self.onSelectValueLabelNumber)
    #   Generate Mesh Parameters
    #   Parameters to SPHARM Mesh
    #   Visualization
    #   Apply CLIs
    self.applyButton.connect('clicked(bool)', self.onApplyButton)


  def cleanup(self):
    pass

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

  #
  #   Post Processed Segmentation
  #
  def onSelectValueLabelNumber(self):
    self.label_ValueLabelNumber.enabled = self.LabelState.checkState()
    self.ValueLabelNumber.enabled = self.LabelState.checkState()

  #
  #   Apply CLIs
  #
  def onApplyButton(self):
    self.callSegPostProcess()
    self.callGenParaMesh()
    self.callParaToSPHARMMesh()

  def callSegPostProcess(self):
    #     Creation of the parameters
    parameters = {}

    inputList = list()
    inputDirectory = self.GroupProjectInputDirectory.directory.encode('utf-8')
    for file in os.listdir(inputDirectory):
      if file.endswith(".gipl") or file.endswith(".gipl.gz"):
        filepath = inputDirectory + '/' + file
        inputList.append(filepath)
    slicer.util.loadLabelVolume(inputList[0])
    labelMapVolumeNode_list = slicer.mrmlScene.GetNodesByClass("vtkMRMLLabelMapVolumeNode")
    volume = labelMapVolumeNode_list.GetItemAsObject(0)
    parameters["fileName"] = slicer.mrmlScene.GetNodesByName(volume.GetName()).GetItemAsObject(0)

    output_node = slicer.mrmlScene.AddNode(slicer.vtkMRMLLabelMapVolumeNode())
    output_node.SetName("output_PostProcess")
    parameters["outfileName"] = output_node.GetID()

    #     Call the CLI
    print "Call: SegPostProcess"
    SegPostProcess = slicer.modules.segpostprocessclp
    slicer.cli.run(SegPostProcess, None, parameters, wait_for_completion=True)
    slicer.util.saveNode(output_node, slicer.app.temporaryPath + "/outputPostProcess.gipl")

  def callGenParaMesh(self):
    #     Creation of the parameters
    parameters = {}
    parameters["infile"] = slicer.mrmlScene.GetNodesByName("output_PostProcess").GetItemAsObject(0)

    output_para_model = slicer.mrmlScene.AddNode(slicer.vtkMRMLModelNode())
    output_para_model.SetName("output_para")
    parameters["outParaName"] = output_para_model

    output_surfmesh_model = slicer.mrmlScene.AddNode(slicer.vtkMRMLModelNode())
    output_surfmesh_model.SetName("output_surfmesh")
    parameters["outSurfName"] = output_surfmesh_model

    parameters["numIterations"] = "50"

    #     Call the CLI
    print "Call: GenParaMesh"
    GenParaMesh = slicer.modules.genparameshclp
    slicer.cli.run(GenParaMesh, None, parameters, wait_for_completion=True)
    slicer.util.saveNode(output_para_model, slicer.app.temporaryPath + "/Parameterization.vtk")
    slicer.util.saveNode(output_surfmesh_model, slicer.app.temporaryPath + "/SurfaceMesh.vtk")

  def callParaToSPHARMMesh(self):
    #     Creation of the parameters
    parameters = {}
    # list = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    parameters["inParaFile"] = slicer.mrmlScene.GetNodesByName("output_para").GetItemAsObject(0)
    parameters["inSurfFile"] = slicer.mrmlScene.GetNodesByName("output_surfmesh").GetItemAsObject(0)

    outputDirectory = self.GroupProjectOutputDirectory.directory.encode('utf-8')
    parameters["outbase"] = outputDirectory + "/test"
    #     Call the CLI
    print "Call: ParaToSPHARMMesh"
    ParaToSPHARMMesh = slicer.modules.paratospharmmeshclp
    slicer.cli.run(ParaToSPHARMMesh, None, parameters, wait_for_completion=True)

#
# ShapeAnalysisModuleLogic
#

class ShapeAnalysisModuleLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  pass




class ShapeAnalysisModuleTest(ScriptedLoadableModuleTest):
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
    self.delayDisplay(' Tests Passed! ')
